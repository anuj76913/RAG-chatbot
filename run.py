import subprocess
import os
import sys

def main():
    # Suppress the Streamlit welcome/email prompt
    os.environ["STREAMLIT_EMAIL"] = ""
    
    print("Starting Streamlit app locally...")
    # Start the Streamlit app
    app = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    try:
        app.wait()
    except KeyboardInterrupt:
        print("Shutting down app...")
        app.terminate()

if __name__ == "__main__":
    main()
