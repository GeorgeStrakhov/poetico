from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.responses import FileResponse
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

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Create a sub-application for API routes
api_app = FastAPI()

# Update CORS to only allow our own origin
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8888"],
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
DATA_DIR = Path("data")
POEMS_DIR = DATA_DIR / "poems"
DATA_DIR.mkdir(exist_ok=True)
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

# Move all API routes to api_app
@api_app.post("/generate_line", response_model=GenerateResponse)
async def generate_lines(request: GenerateRequest):
    logger.debug(f"Received generate request with text: {request.current_text}")
    temperatures = [0.1, 0.5, 0.9, 1.2, 1.5]
    
    try:
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=5) as executor:
            partial_generate = functools.partial(generate_line, request.current_text)
            alternatives = list(executor.map(partial_generate, temperatures))
            
        return GenerateResponse(alternatives=alternatives, temperatures=temperatures)
    except Exception as e:
        logger.error(f"Error in generate_lines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_app.post("/record_preference")
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
    if not PREFERENCES_FILE.exists():
        raise HTTPException(status_code=404, detail="No preferences file found")
    return FileResponse(
        PREFERENCES_FILE,
        media_type="application/json",
        filename="line_preferences.jsonl"
    )

# New endpoint to save poem
@api_app.post("/save_poem")
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
        for path in POEMS_DIR.glob(f"*-{poem_id}-*.txt"):
            with open(path) as f:
                content = f.read()
            return {"content": content}
            
        raise HTTPException(status_code=404, detail="Poem not found")
    except Exception as e:
        logger.error(f"Error loading poem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount the API routes first
app.mount("/api", api_app)

# Add this before mounting the static files
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Skip API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for all other routes
    return FileResponse("frontend/index.html")

# Then mount the static files (but not at root anymore)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Function to open browser
def open_browser():
    webbrowser.open("http://localhost:8888")

# Startup event
@app.on_event("startup")
async def startup_event():
    Timer(1.5, open_browser).start() 