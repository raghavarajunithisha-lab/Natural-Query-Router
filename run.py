import uvicorn
import subprocess
import threading
import sys
from dotenv import load_dotenv
import os

def start_fastapi():
    print("Starting FastAPI Backend on port 8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

def start_mcp():
    print("Starting MCP Server...")
    try:
        subprocess.run([sys.executable, "app/mcp_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"MCP Server exited with error: {e}")

if __name__ == "__main__":
    load_dotenv()
    
    # Run FastAPI in the main thread
    # The MCP server usually runs on a separate CLI or stdio pipe. 
    # For dev purposes, we can just run the FastAPI server, as FastMCP can be started separately.
    
    # To start both locally for demo:
    # mcp_thread = threading.Thread(target=start_mcp, daemon=True)
    # mcp_thread.start()
    
    start_fastapi()
