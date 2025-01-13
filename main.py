import uvicorn
import subprocess
import sys
import os
from threading import Thread

def run_frontend_dev():
    os.chdir("frontend")
    subprocess.run(["npm", "run", "dev"], check=True)

def run_backend(dev_mode=True):
    os.environ["DEV_MODE"] = str(dev_mode).lower()
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8888, reload=dev_mode)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    
    if mode == "dev":
        # Run frontend and backend in development mode
        frontend_thread = Thread(target=run_frontend_dev)
        frontend_thread.start()
        run_backend(dev_mode=True)
        
    else:
        # In production, just run the backend (which serves the built frontend)
        run_backend(dev_mode=False)
