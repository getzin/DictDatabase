import subprocess
import sys
import time

### API Key: da4ed685f6765aef210f10d67ba49bc221f8b1eaa7215ddabba99ff4e310fc6f

# Start FastAPI backend
backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"]
    )

# Wait a moment to let FastAPI start
time.sleep(2)

# Start Streamlit frontend
try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])
except KeyboardInterrupt:
        print("\n🛑 shutting down...")
finally:
        backend.terminate()
        try:
            backend.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend.kill()
        print("-✅ everything has shut down!\n")