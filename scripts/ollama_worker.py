"""Read one image through Ollama and keep the actual model settings with its answer.
The streaming connection closes if the parent stops this worker after a timeout.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import base64
import hashlib
import io
import json
import time

import httpx
from PIL import Image


def get_json(client, path, body=None):
    response = client.get(path) if body is None else client.post(path, json=body)
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data


def run(request):
    model = request["model"]
    tag = model["tag"]
    with httpx.Client(
        base_url=request["ollama_url"],
        timeout=httpx.Timeout(request["timeout_seconds"], connect=5),
        trust_env=False,
    ) as client:
        version = get_json(client, "/api/version")["version"]
        tags = get_json(client, "/api/tags")["models"]
        installed = next((item for item in tags if item["name"] == tag), None)
        if installed is None:
            raise RuntimeError("The requested local model is not installed.")
        if model.get("digest") and model["digest"] != installed["digest"]:
            raise RuntimeError("The local model digest has changed; review the registry first.")
        details = get_json(client, "/api/show", {"model": tag})
        if "vision" not in details.get("capabilities", []):
            raise RuntimeError("This local model does not report vision capability.")

        # A prior request must not leave a warm model or prompt cache in a timed run.
        get_json(client, "/api/generate", {"model": tag, "keep_alive": 0, "stream": False})
        deadline = time.monotonic() + 10
        while any(item["name"] == tag for item in get_json(client, "/api/ps")["models"]):
            if time.monotonic() > deadline:
                raise RuntimeError("The previous model could not unload before this run.")
            time.sleep(0.1)

        with Image.open(request["image_path"]) as source:
            image = source.convert("RGB")
        image.thumbnail((512, 512))
        encoded = io.BytesIO()
        image.save(encoded, "PNG")
        pixels = encoded.getvalue()
        options = {
            "temperature": 0,
            "seed": 42,
            "num_predict": request["max_new_tokens"],
            "num_ctx": 4096,
            "num_thread": 4,
            "num_gpu": 0,
        }
        body = {
            "model": tag,
            "messages": [
                {
                    "role": "user",
                    "content": request["prompt"],
                    "images": [base64.b64encode(pixels).decode()],
                }
            ],
            "stream": True,
            "options": options,
            "keep_alive": 0,
        }
        pieces = []
        final = None
        with client.stream("POST", "/api/chat", json=body) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("error"):
                    raise RuntimeError(chunk["error"])
                pieces.append(chunk.get("message", {}).get("content", ""))
                if chunk.get("done"):
                    final = chunk
        if final is None:
            raise RuntimeError("Ollama disconnected before the answer was complete.")
        quantization = installed.get("details", {}).get("quantization_level", "unknown")
        return {
            "text": "".join(pieces).strip(),
            "load_ms": round(final.get("load_duration", 0) / 1e6),
            "generation_ms": round(final.get("eval_duration", 0) / 1e6),
            "prompt_eval_ms": round(final.get("prompt_eval_duration", 0) / 1e6),
            "server_total_ms": round(final.get("total_duration", 0) / 1e6),
            "output_tokens": final.get("eval_count"),
            "input_tokens": final.get("prompt_eval_count"),
            "done_reason": final.get("done_reason"),
            "peak_rss_mb": None,
            "memory_note": "The Ollama API does not report a process peak. Client memory would exclude the model runner, so it is not used.",
            "device": f"CPU · 4 threads · {quantization}",
            "runtime": "ollama",
            "runtime_version": f"ollama {version}",
            "model_tag": tag,
            "model_digest": installed["digest"],
            "quantization": quantization,
            "model_details": installed.get("details", {}),
            "options": options,
            "image_preprocessing": {
                "version": "ollama-thumbnail-512-v1",
                "longest_edge": 512,
                "sent_dimensions": list(image.size),
                "sent_png_sha256": hashlib.sha256(pixels).hexdigest(),
                "note": "RGB PNG thumbnail with preserved aspect ratio; native Qwen vision preprocessing is handled by this Ollama version.",
            },
        }
