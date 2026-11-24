"""Install or start Imarah's own Ollama copy, keeping models inside this project.
Use: python scripts/ollama_local.py install | serve | pull qwen3-vl-2b
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.34.2"
ARCHIVE_SHA = "e155b83589986d2c581fdbf1381ea3ebdb16549883679cd5a0627f7cdc05b12b"
LOCAL_URL = "http://127.0.0.1:11435"
BINARY = ROOT / ".runtime/ollama/bin/ollama"


def environment():
    return {
        **os.environ,
        "OLLAMA_HOST": "127.0.0.1:11435",
        "OLLAMA_MODELS": str(ROOT / "models/ollama"),
        "OLLAMA_MAX_LOADED_MODELS": "1",
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_CONTEXT_LENGTH": "4096",
        "OLLAMA_NO_CLOUD": "1",
        "OLLAMA_NOPRUNE": "1",
    }


def version():
    try:
        response = httpx.get(LOCAL_URL + "/api/version", timeout=1, trust_env=False)
        response.raise_for_status()
        return response.json()["version"]
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def ensure_server():
    """Return only a child started here, so we never stop someone else's process."""
    configured_url = os.getenv("OLLAMA_URL", "").strip().rstrip("/") or LOCAL_URL
    if configured_url != LOCAL_URL:
        return None
    if version() or not BINARY.exists():
        return None
    (ROOT / ".runtime").mkdir(exist_ok=True)
    with (ROOT / ".runtime/ollama.log").open("ab") as log:
        process = subprocess.Popen(
            [str(BINARY), "serve"],
            env=environment(),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
        )
    for _ in range(100):
        if version():
            print(f"Local vision server ready at {LOCAL_URL}", flush=True)
            return process
        if process.poll() is not None:
            break
        time.sleep(0.1)
    stop_child(process)
    raise RuntimeError("The local vision server did not start. Read .runtime/ollama.log.")


def stop_child(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def install(archive=None):
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        raise SystemExit(
            "The bundled installer supports Linux x86_64. See docs/guides/local-qwen.md for Windows and macOS."
        )
    if version():
        raise SystemExit("Stop the project vision server before replacing its runtime.")
    destination = ROOT / ".runtime/ollama"
    archive = (
        Path(archive)
        if archive
        else ROOT / f".runtime/downloads/ollama-linux-amd64-{VERSION}.tar.zst"
    )
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        if shutil.disk_usage(ROOT).free < 3 * 1024**3:
            raise SystemExit("Keep at least 3 GiB free for the runtime download and extraction.")
        if not shutil.which("curl"):
            raise SystemExit("Install curl, or pass an already downloaded archive with --archive.")
        partial = archive.with_suffix(archive.suffix + ".partial")
        subprocess.run(
            [
                "curl",
                "-fL",
                "--retry",
                "5",
                "-C",
                "-",
                "-o",
                str(partial),
                f"https://github.com/ollama/ollama/releases/download/v{VERSION}/ollama-linux-amd64.tar.zst",
            ],
            check=True,
        )
        partial.replace(archive)
    sha = hashlib.sha256()
    with archive.open("rb") as file:
        for block in iter(lambda: file.read(4 * 1024 * 1024), b""):
            sha.update(block)
    if sha.hexdigest() != ARCHIVE_SHA:
        raise SystemExit(
            "Runtime SHA256 does not match the pinned official release. Nothing was installed."
        )
    if not shutil.which("zstd"):
        raise SystemExit("Install zstd to extract this official archive.")
    destination.mkdir(parents=True, exist_ok=True)
    # CPU evaluation needs the executable and CPU libraries, not the bundled GPU libraries.
    subprocess.run(
        [
            "tar",
            "--zstd",
            "-xf",
            str(archive),
            "-C",
            str(destination),
            "--exclude=lib/ollama/cuda*",
            "--exclude=lib/ollama/vulkan*",
            "--exclude=lib/ollama/mlx*",
        ],
        check=True,
    )
    print(f"Verified Ollama {VERSION} installed at {destination}")


def pull(model_id):
    registry = json.loads((ROOT / "models/registry.json").read_text())
    model = next(
        (item for item in registry if item["id"] == model_id and item["runtime"] == "ollama"), None
    )
    if not model:
        raise SystemExit("Choose an Ollama model ID from models/registry.json.")
    if shutil.disk_usage(ROOT).free < model.get("download_bytes", 6 * 1024**3) + 2 * 1024**3:
        raise SystemExit(
            "There is not enough free disk space for this model plus 2 GiB of working room."
        )
    if not version():
        raise SystemExit("Start the project server first: python scripts/ollama_local.py serve")
    executable = str(BINARY) if BINARY.exists() else shutil.which("ollama")
    if not executable:
        raise SystemExit("Install Ollama before pulling a model.")
    subprocess.run([executable, "pull", model["tag"]], env=environment(), check=True)
    response = httpx.get(LOCAL_URL + "/api/tags", timeout=5, trust_env=False)
    response.raise_for_status()
    local = next(item for item in response.json()["models"] if item["name"] == model["tag"])
    if model.get("digest") and local["digest"] != model["digest"]:
        raise SystemExit(
            "Download finished, but upstream changed this tag. Compare its digest before updating the registry; the app will keep it disabled."
        )
    print("Installed digest:", local["digest"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["install", "serve", "pull"])
    parser.add_argument("model_id", nargs="?")
    parser.add_argument("--archive")
    args = parser.parse_args()
    if args.command == "install":
        install(args.archive)
    elif args.command == "pull":
        pull(args.model_id)
    else:
        if version():
            print(f"The project model server is already running at {LOCAL_URL}.")
            return
        executable = str(BINARY) if BINARY.exists() else shutil.which("ollama")
        if not executable:
            raise SystemExit("Install the local runtime first.")
        print(f"Serving local models at {LOCAL_URL}. Keep this terminal open.", flush=True)
        try:
            subprocess.run([executable, "serve"], env=environment(), check=True)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
