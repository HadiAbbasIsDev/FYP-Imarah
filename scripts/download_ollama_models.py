"""Download pinned Qwen models in small pieces that survive a broken connection.
Use: python scripts/download_ollama_models.py --models qwen3-vl-2b qwen3-vl-4b
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "https://registry.ollama.ai/v2/library"
CHUNK_BYTES = 4 * 1024 * 1024


def file_sha256(path):
    sha = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(CHUNK_BYTES), b""):
            sha.update(block)
    return sha.hexdigest()


def save_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2))
    temporary.replace(path)


def download_layer(url, destination, size, sha, work, workers=3):
    """Only publish a completed file after its official hash matches."""
    if destination.exists():
        if destination.stat().st_size == size and file_sha256(destination) == sha:
            print("Already verified:", destination.name[:24], flush=True)
            return
        raise ValueError(
            "An existing model layer has the wrong hash. Inspect it before replacing it."
        )
    work.mkdir(parents=True, exist_ok=True)
    partial = work / f"{sha}.part"
    checkpoint = work / f"{sha}.json"
    total_chunks = (size + CHUNK_BYTES - 1) // CHUNK_BYTES
    completed = set()
    if checkpoint.exists() and partial.exists():
        saved = json.loads(checkpoint.read_text())
        if saved["size"] != size or saved["chunk_bytes"] != CHUNK_BYTES or saved["sha256"] != sha:
            raise ValueError("Download checkpoint does not match the requested layer.")
        completed = set(saved["completed_chunks"])
        if any(not isinstance(n, int) or not 0 <= n < total_chunks for n in completed):
            raise ValueError("Download checkpoint contains invalid chunk numbers.")
    lock = threading.Lock()
    cancelled = threading.Event()
    handle = partial.open("r+b" if partial.exists() else "w+b")
    handle.truncate(size)
    client = httpx.Client(
        follow_redirects=True,
        timeout=httpx.Timeout(60, connect=20),
        limits=httpx.Limits(max_connections=workers * 2, max_keepalive_connections=workers * 2),
    )

    def chunk(number):
        first = number * CHUNK_BYTES
        last = min(first + CHUNK_BYTES, size) - 1
        for attempt in range(12):
            if cancelled.is_set():
                return
            try:
                with client.stream(
                    "GET",
                    url,
                    headers={"Range": f"bytes={first}-{last}", "Accept-Encoding": "identity"},
                ) as response:
                    response.raise_for_status()
                    if (
                        response.status_code != 206
                        or response.headers.get("content-range") != f"bytes {first}-{last}/{size}"
                    ):
                        raise ValueError(
                            "The download server did not return the exact requested range."
                        )
                    content = bytearray()
                    for block in response.iter_bytes(128 * 1024):
                        if cancelled.is_set():
                            return
                        content.extend(block)
                        if len(content) > last - first + 1:
                            raise ValueError("A downloaded chunk exceeds its requested size.")
                    if len(content) != last - first + 1:
                        raise ValueError("A downloaded chunk is incomplete.")
                with lock:
                    handle.seek(first)
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                    # Save only completed chunks. Retrying can lose at most one small piece.
                    completed.add(number)
                    save_json(
                        checkpoint,
                        {
                            "sha256": sha,
                            "size": size,
                            "chunk_bytes": CHUNK_BYTES,
                            "completed_chunks": sorted(completed),
                        },
                    )
                    print(f"{sha[:12]}: {len(completed)}/{total_chunks} pieces saved", flush=True)
                return
            except httpx.HTTPError:
                if attempt == 11:
                    raise
                time.sleep(min(attempt + 1, 5))

    try:
        missing = [number for number in range(total_chunks) if number not in completed]
        pool = ThreadPoolExecutor(max_workers=workers)
        try:
            futures = [pool.submit(chunk, number) for number in missing]
            for future in futures:
                future.result()
        except BaseException:
            cancelled.set()
            raise
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
    finally:
        handle.close()
        client.close()
    if file_sha256(partial) != sha:
        # The final hash protects against a corrupt file or checkpoint as well as bad transfers.
        checkpoint.unlink(missing_ok=True)
        raise ValueError(
            "Final layer SHA256 mismatch. No model was activated; retry to download fresh pieces."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial.replace(destination)
    checkpoint.unlink(missing_ok=True)
    print("Verified complete layer:", sha, flush=True)


def download_model(model_id):
    models = json.loads((ROOT / "models/registry.json").read_text())
    model = next((item for item in models if item["id"] == model_id), None)
    if not model or model["runtime"] != "ollama" or not model.get("digest"):
        raise ValueError("Choose an Ollama model with a pinned digest in models/registry.json.")
    if not re.fullmatch(r"[a-z0-9_-]+:[a-z0-9_.-]+", model["tag"]):
        raise ValueError("This downloader supports ordinary public library model tags.")
    name, tag = model["tag"].split(":")
    response = httpx.get(f"{REGISTRY}/{name}/manifests/{tag}", timeout=30)
    response.raise_for_status()
    manifest_bytes = response.content
    if hashlib.sha256(manifest_bytes).hexdigest() != model["digest"]:
        raise ValueError(
            "Upstream changed this tag. Review its new manifest before updating the pinned digest."
        )
    manifest = json.loads(manifest_bytes)
    store = ROOT / "models/ollama"
    work = ROOT / ".runtime/model-downloads"
    layers = {layer["digest"]: layer for layer in [manifest["config"], *manifest["layers"]]}
    missing_bytes = sum(
        layer["size"]
        for sha, layer in layers.items()
        if not (store / "blobs" / sha.replace(":", "-")).exists()
    )
    if shutil.disk_usage(ROOT).free < missing_bytes + 1024**3:
        raise ValueError(
            "Keep enough free disk space for the missing layers plus 1 GiB of working room."
        )
    for digest, layer in layers.items():
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
            raise ValueError("Invalid layer digest in the manifest.")
        download_layer(
            f"{REGISTRY}/{name}/blobs/{digest}",
            store / "blobs" / digest.replace(":", "-"),
            layer["size"],
            digest.split(":")[1],
            work,
        )
    destination = store / "manifests/registry.ollama.ai/library" / name / tag
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    temporary.write_bytes(manifest_bytes)
    temporary.replace(destination)
    print(f"Ready: {model['tag']} · {model['digest']}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=["qwen3-vl-2b", "qwen3-vl-4b"])
    args = parser.parse_args()
    for model_id in args.models:
        download_model(model_id)


if __name__ == "__main__":
    main()
