import subprocess
import os
import sys

def main():
    # Suppress the Streamlit welcome/email prompt
    os.environ["STREAMLIT_EMAIL"] = ""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(base_dir, "venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable

    print(f"Starting Streamlit app locally with {python_exe}...")
    # Start the Streamlit app
    app = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"],
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
