from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.responses import FileResponse, StreamingResponse
import webbrowser
from threading import Timer
from loguru import logger
import asyncio
from asyncio import TimeoutError
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
import functools
from datetime import datetime
from slugify import slugify
import glob
import random
import zipfile
import io

# Load environment variables
load_dotenv()

AUTHOR_SECRET = os.getenv("AUTHOR_SECRET")
if not AUTHOR_SECRET:
    raise Exception("AUTHOR_SECRET environment variable is required")

async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        if token != AUTHOR_SECRET:
            raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

# Check if we're in development mode
IS_DEV = os.getenv("DEV_MODE", "true").lower() == "true"

# Initialize FastAPI app
app = FastAPI()

# Create a sub-application for API routes
api_app = FastAPI()

# Update CORS to allow both development and production origins
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8888", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.getenv("FIREWORKS_API_KEY"),
)

# Ensure data directory exists
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data"
POEMS_DIR = DATA_DIR / "poems"
DATA_DIR.mkdir(exist_ok=True)
POEMS_DIR.mkdir(exist_ok=True)
PREFERENCES_FILE = DATA_DIR / "line_preferences.jsonl"

# Configure logger
logger.add("debug.log", rotation="500 MB", level="DEBUG")

# Models for request/response
class GenerateRequest(BaseModel):
    current_text: str

class GenerateResponse(BaseModel):
    alternatives: List[str]
    temperatures: List[float]

class PreferenceRecord(BaseModel):
    current_text: str
    alternatives: List[str]
    chosen: str

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Helper function to generate a line with timeout
def generate_line(text: str, temperature: float) -> str:
    try:
        completion = client.completions.create(
            model="accounts/george-strakhov-3cfc5a/models/poetry-continuation-v1",
            prompt=f"Continue the following poem:\n{text}\n",
            max_tokens=100,
            temperature=temperature,
            stop=["\n"],
        )
        return completion.choices[0].text
    except Exception as e:
        logger.error(f"Error generating line: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to randomly truncate text
def randomly_truncate_text(text: str) -> str:
    lines = text.strip().split('\n')
    if len(lines) <= 1:
        return text
    
    # Randomly decide how many lines to keep (at least 1)
    keep_lines = random.randint(1, min(3, len(lines)))
    return '\n'.join(lines[-keep_lines:])

# Protected routes require token
@api_app.post("/generate_line", dependencies=[Depends(verify_token)])
async def generate_lines(request: GenerateRequest):
    logger.debug(f"Received generate request with text: {request.current_text}")
    
    # Generate initial temperatures between 0.1 and 1.5
    temperatures = [round(random.uniform(0.1, 1.5), 2) for _ in range(5)]
    
    try:
        unique_alternatives = set()
        final_alternatives = []
        final_temperatures = []
        max_attempts = 10  # Prevent infinite loops
        attempt = 0
        
        while len(unique_alternatives) < 5 and attempt < max_attempts:
            # Use ThreadPoolExecutor for concurrent execution
            with ThreadPoolExecutor(max_workers=5) as executor:
                # For each missing alternative, generate a new one
                remaining = 5 - len(unique_alternatives)
                
                # For each generation, randomly decide whether to truncate the text
                texts = [
                    randomly_truncate_text(request.current_text) if random.random() < 0.7 
                    else request.current_text 
                    for _ in range(remaining)
                ]
                
                # For re-rolls, use higher temperatures
                new_temps = [
                    round(random.uniform(0.5 + (attempt * 0.2), 1.5 + (attempt * 0.2)), 2)
                    for _ in range(remaining)
                ]
                
                # Create tasks with different texts and temperatures
                tasks = [
                    (text, temp) for text, temp in zip(texts, new_temps)
                ]
                
                new_alternatives = list(executor.map(lambda x: generate_line(*x), tasks))
                
                # Add new unique alternatives
                for alt, temp in zip(new_alternatives, new_temps):
                    if alt not in unique_alternatives:
                        unique_alternatives.add(alt)
                        final_alternatives.append(alt)
                        final_temperatures.append(temp)
                        if len(unique_alternatives) == 5:
                            break
            
            attempt += 1
        
        if len(final_alternatives) < 5:
            logger.warning(f"Could only generate {len(final_alternatives)} unique alternatives after {attempt} attempts")
        
        return GenerateResponse(alternatives=final_alternatives, temperatures=final_temperatures)
    except Exception as e:
        logger.error(f"Error in generate_lines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_app.post("/record_preference", dependencies=[Depends(verify_token)])
async def record_preference(preference: PreferenceRecord):
    logger.debug(f"Recording preference: {preference}")
    try:
        with open(PREFERENCES_FILE, "a") as f:
            f.write(json.dumps(preference.dict()) + "\n")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error recording preference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_app.get("/download_preferences")
async def download_preferences():
    try:
        if not PREFERENCES_FILE.exists():
            raise HTTPException(status_code=404, detail="No preferences file found")
            
        return FileResponse(
            PREFERENCES_FILE,
            media_type="application/x-jsonlines",
            filename="line_preferences.jsonl"
        )
    except Exception as e:
        logger.error(f"Error downloading preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint to save poem
@api_app.post("/save_poem", dependencies=[Depends(verify_token)])
async def save_poem(poem: dict):
    try:
        content = poem.get("content", "").strip()
        poem_id = poem.get("id")
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty poem")
            
        if not poem_id:
            raise HTTPException(status_code=400, detail="No poem ID provided")
            
        first_line = content.split('\n')[0][:50]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}-{poem_id}-{slugify(first_line)}.txt"
        
        poem_path = POEMS_DIR / filename
        POEMS_DIR.mkdir(exist_ok=True)
        
        # Remove old versions of this poem if they exist
        for old_path in POEMS_DIR.glob(f"*-{poem_id}-*.txt"):
            old_path.unlink()
        
        with open(poem_path, "w") as f:
            f.write(content)
            
        return {"status": "success", "id": poem_id}
    except Exception as e:
        logger.error(f"Error saving poem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Update list poems endpoint to parse new filename format
@api_app.get("/list_poems")
async def list_poems():
    try:
        poems_dir = POEMS_DIR
        poems_dir.mkdir(exist_ok=True)
        poems = []
        
        for path in sorted(poems_dir.glob("*.txt"), reverse=True):
            try:
                # Parse filename parts (timestamp-id-slug.txt)
                filename_parts = path.stem.split('-', 2)  # Split into [timestamp, id, slug]
                if len(filename_parts) >= 2:
                    # Get timestamp from the first part (no need to split again)
                    timestamp = datetime.strptime(filename_parts[0], "%Y%m%d%H%M%S")
                    poem_id = filename_parts[1]
                    
                    with open(path) as f:
                        first_line = f.readline().strip()
                    
                    poems.append({
                        "id": poem_id,
                        "first_line": first_line,
                        "created": timestamp.isoformat(),
                        "filename": path.name
                    })
            except Exception as e:
                logger.warning(f"Skipping malformed poem file {path}: {str(e)}")
                continue
        
        return poems
    except Exception as e:
        logger.error(f"Error listing poems: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Update get poem endpoint to handle new filename format
@api_app.get("/poem/{poem_id}")
async def get_poem(poem_id: str):
    try:
        # Look for any file containing the poem_id in the middle part
        found = False
        for path in POEMS_DIR.glob(f"*-{poem_id}-*.txt"):
            found = True
            with open(path) as f:
                content = f.read()
            return {"content": content}
            
        if not found:
            raise HTTPException(status_code=404, detail="Poem not found")
            
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without catching them
        raise
    except Exception as e:
        logger.error(f"Error loading poem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add delete poem endpoint
@api_app.delete("/poem/{poem_id}", dependencies=[Depends(verify_token)])
async def delete_poem(poem_id: str):
    try:
        deleted = False
        # Look for any file containing the poem_id in the middle part
        for path in POEMS_DIR.glob(f"*-{poem_id}-*.txt"):
            path.unlink()
            deleted = True
            
        if not deleted:
            raise HTTPException(status_code=404, detail="Poem not found")
            
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deleting poem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Public routes don't require token
@api_app.get("/download_poems_zip")
async def download_poems_zip():
    try:
        # Create a BytesIO object to store the zip file
        zip_buffer = io.BytesIO()
        
        # Create a new zip file
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all poem files to the zip
            for poem_path in POEMS_DIR.glob("*.txt"):
                # Read the poem file
                with open(poem_path, 'r') as poem_file:
                    content = poem_file.read()
                    # Add the file to the zip with its name
                    zip_file.writestr(poem_path.name, content)
        
        # Seek to the beginning of the BytesIO buffer
        zip_buffer.seek(0)
        
        # Return the zip file as a streaming response
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=gspoems.zip"}
        )
    except Exception as e:
        logger.error(f"Error creating zip file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount the API routes first
app.mount("/api", api_app)

# In production mode, serve the built frontend
if not IS_DEV:
    # Check if the dist directory exists
    dist_path = Path("frontend/dist")
    assets_path = dist_path / "assets"
    if dist_path.exists() and assets_path.exists():
        # Serve static files from the Vue build directory
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")
        
        @app.get("/{full_path:path}")
        async def catch_all(full_path: str):
            # Skip API routes
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not found")
            
            # Serve index.html for all other routes
            return FileResponse(str(dist_path / "index.html"))
else:
    # In development mode, we don't need to serve the frontend
    # as it's handled by the Vite dev server
    @app.get("/")
    async def dev_mode_notice():
        return {"message": "API server running in development mode. Frontend is served at http://localhost:3000"}

# Function to open browser
def open_browser():
    port = 3000 if IS_DEV else 8888
    webbrowser.open(f"http://localhost:{port}")

# Startup event
@app.on_event("startup")
async def startup_event():
    Timer(1.5, open_browser).start() 