"""
run_app.py — FakeShield Launcher
==================================
Convenience entry point. Does the following in order:
  1. Checks if trained model files exist
  2. If not, runs training automatically
  3. Starts the Flask web application

Usage:
    python run_app.py              # Default: http://localhost:5000
    python run_app.py --port 8080  # Custom port
    python run_app.py --no-train   # Skip training check
"""

import os
import sys
import argparse
import subprocess

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "fake_news_model.pkl")
VEC_PATH   = os.path.join(BASE_DIR, "ml_models", "vectorizer.pkl")
TRAIN_SCRIPT = os.path.join(BASE_DIR, "ml_models", "train_and_save.py")


def models_ready() -> bool:
    """Check if required model files exist."""
    return os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH)


def train_models():
    """Run the training script in a subprocess."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║  Models not found — running trainer first…           ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    result = subprocess.run(
        [sys.executable, TRAIN_SCRIPT],
        cwd=BASE_DIR,
    )
    if result.returncode != 0:
        print("\n[ERROR] Training failed. Please check errors above.")
        sys.exit(1)
    print("\n✅ Training complete!\n")


def start_app(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Import and run the Flask app."""
    sys.path.insert(0, BASE_DIR)

    print("╔══════════════════════════════════════════════════════╗")
    print("║       FakeShield — Fake News Detection Platform      ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  🌐  Open: http://127.0.0.1:{port}")
    print(f"  📡  API:  http://127.0.0.1:{port}/predict")
    print(f"  ❤️   Health: http://127.0.0.1:{port}/health")
    print("  Press Ctrl+C to stop\n")

    from app import app
    app.run(host=host, port=port, debug=debug)


def main():
    parser = argparse.ArgumentParser(description="FakeShield — Fake News Detection Platform")
    parser.add_argument("--port",     type=int,  default=5000, help="Port to run on (default: 5000)")
    parser.add_argument("--host",     type=str,  default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug",    action="store_true", help="Enable Flask debug mode")
    parser.add_argument("--no-train", action="store_true", help="Skip auto-training check")
    args = parser.parse_args()

    if not args.no_train and not models_ready():
        train_models()

    start_app(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
