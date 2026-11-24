"""Download our two small VLMs without filling the disk or running remote code.

Use: python scripts/download_models.py [smolvlm-256m smolvlm-500m]
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json
import shutil
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
models = json.loads((ROOT / "models/registry.json").read_text())
selected = sys.argv[1:] or ["smolvlm-256m", "smolvlm-500m"]
for model_id in selected:
    model = next((m for m in models if m["id"] == model_id), None)
    if not model or model["runtime"] != "transformers":
        raise SystemExit(f"Unsupported download: {model_id}. See models/README.md.")
    target = ROOT / "models" / model_id
    if (target / "model.safetensors").exists():
        print(
            f"{model_id}: weights already present; verifying supporting files.",
            flush=True,
        )
    elif shutil.disk_usage(ROOT).free < model["download_bytes"] + 900_000_000:
        raise SystemExit(f"Not enough free space for {model_id}; keep at least 900 MB spare.")
    print(f"Downloading {model['repository']} at {model['revision']}", flush=True)
    snapshot_download(
        repo_id=model["repository"],
        revision=model["revision"],
        local_dir=target,
        allow_patterns=["*.json", "*.txt", "*.safetensors", "*.md"],
        max_workers=2,
    )
    (target / "READY").write_text(model["revision"] + "\n")
    print(f"Ready: {target}", flush=True)
