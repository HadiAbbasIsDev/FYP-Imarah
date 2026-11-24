"""Check the local Ollama server before offering its vision models in the app.
This never downloads a model or sends a photograph during discovery.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import os
import re

import httpx


def server_url():
    return os.getenv("OLLAMA_URL", "").strip().rstrip("/") or "http://127.0.0.1:11435"


def read_catalog():
    """Read the installed tags once; a stopped server is an ordinary setup state."""
    try:
        with httpx.Client(base_url=server_url(), timeout=2, trust_env=False) as client:
            response = client.get("/api/version")
            response.raise_for_status()
            version = response.json()["version"]
            numbers = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
            if not numbers or tuple(map(int, numbers.groups())) < (0, 12, 7):
                return {}, "Ollama 0.12.7 or newer is needed for the Qwen3-VL shortlist."
            response = client.get("/api/tags")
            response.raise_for_status()
            return {model["name"]: model for model in response.json()["models"]}, None
    except (httpx.HTTPError, httpx.InvalidURL, ValueError, KeyError, TypeError):
        return {}, "Start the local model server: python scripts/ollama_local.py serve"


def model_status(model, catalog, error):
    if error:
        return {"installed": False, "availability_note": error}
    local = catalog.get(model["tag"])
    if not local:
        return {"installed": False, "availability_note": "Model download pending."}
    digest = local.get("digest")
    if model.get("digest") and digest != model["digest"]:
        return {
            "installed": False,
            "availability_note": "Local model differs from the recorded digest. Check the model setup guide.",
        }
    return {
        "installed": True,
        "availability_note": "Local model server is ready. Vision capability is checked before inference.",
        "local_digest": digest,
        "quantization": local.get("details", {}).get("quantization_level"),
        "download_bytes": local.get("size"),
    }


def require_model(model):
    catalog, error = read_catalog()
    status = model_status(model, catalog, error)
    if not status["installed"]:
        raise ValueError(status["availability_note"])
    return catalog[model["tag"]]
