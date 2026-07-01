import subprocess
import time
import os
import sys

def main():
    # Suppress the Streamlit welcome/email prompt
    os.environ["STREAMLIT_EMAIL"] = ""
    
    print("Starting FastAPI backend...")
    # Start the FastAPI backend
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    # Wait for the backend to start up
    time.sleep(3)
    
    print("Starting Streamlit frontend...")
    # Start the Streamlit frontend
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("Shutting down servers...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()
