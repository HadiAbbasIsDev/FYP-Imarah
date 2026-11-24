"""Start the already-built local app with one command on Windows, Linux or macOS.
Use: python scripts/start.py. Keep the terminal open while demonstrating the app.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
import uvicorn

from backend.app import config  # Loads .env before reading the host and port.
from scripts.ollama_local import ensure_server, stop_child

if not (config.PROJECT / "frontend/dist/index.html").exists():
    raise SystemExit("Build the interface first: cd frontend && npm install && npm run build")
host = os.getenv("IMARAH_HOST", "127.0.0.1")
port = int(os.getenv("IMARAH_PORT", "8000"))
print(f"Imarah.tech is opening at http://{host}:{port}", flush=True)
try:
    model_server = ensure_server()
except (RuntimeError, OSError) as exc:
    model_server = None
    print(f"Local Qwen server needs attention: {exc}", flush=True)
    print("The app will open. Model availability is shown in the model lab.", flush=True)
try:
    uvicorn.run("backend.app.main:app", host=host, port=port, workers=1)
finally:
    stop_child(model_server)
