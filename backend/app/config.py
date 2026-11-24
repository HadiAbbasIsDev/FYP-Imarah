"""Read local settings in one place so the app is easy to move to another PC.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
# Environment variables take priority over the local .env file.
env_file = PROJECT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

DATA = Path(os.getenv("IMARAH_DATA_DIR", str(PROJECT / "data")))
UPLOADS = DATA / "uploads"
RESULTS = Path(os.getenv("IMARAH_RESULTS_DIR", str(PROJECT / "benchmarks/results")))
FIXTURES = PROJECT / "benchmarks/fixtures"
MODELS = json.loads((PROJECT / "models/registry.json").read_text())
MAX_UPLOAD = 10 * 1024 * 1024
for folder in (DATA, UPLOADS, RESULTS):
    folder.mkdir(parents=True, exist_ok=True)
