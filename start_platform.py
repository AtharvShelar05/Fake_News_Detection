import subprocess
import sys
import time

def start_backend():
    print("🚀 Starting Flask Backend (REST API)...")
    return subprocess.Popen([sys.executable, "app.py"])

def start_frontend():
    print("🚀 Starting Streamlit Dashboard (UI)...")
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", "visualization/dashboard.py"])

if __name__ == "__main__":
    try:
        print("======== TruthLens Platform ========")
        backend = start_backend()
        
        # Give the backend a few seconds to load the ML models
        time.sleep(5) 
        
        frontend = start_frontend()
        
        print("\n✅ System is fully running. Press Ctrl+C to shut down.")
        
        # Wait for both processes
        backend.wait()
        frontend.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down TruthLens Platform...")
        backend.terminate()
        frontend.terminate()
        sys.exit(0)
