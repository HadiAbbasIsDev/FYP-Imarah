"""Send Qwen 4B photographs to the VPS through the PC's existing SSH tunnel.
Check the pinned model and preserve its answer; never switch to a local model on failure.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json
import os
import time
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

CONNECTION_HELP = "Qwen VPS is unavailable. Open the SSH tunnel with scripts/connect_qwen_vps.py and keep it running."


class Health(BaseModel):
    status: Literal["ready"]
    model: str
    digest: str
    quantization: str
    runtime: str
    busy: bool


class Answer(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    text: str = Field(min_length=1)
    model: str
    digest: str
    runtime_version: str = Field(min_length=1)
    total_ms: float = Field(ge=0)
    server_total_ms: float = Field(ge=0)
    load_ms: float = Field(ge=0)
    prompt_eval_ms: float = Field(ge=0)
    generation_ms: float = Field(ge=0)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    done_reason: str | None = None
    options: dict[str, float | int]
    image_preprocessing: dict
    loaded_model_bytes: int | None = Field(default=None, ge=0)
    gpu_model_bytes: int | None = Field(default=None, ge=0)


def server_url():
    value = os.getenv("QWEN_VPS_URL", "").strip() or "http://127.0.0.1:18084"
    try:
        url = httpx.URL(value)
        if (
            url.scheme not in ("http", "https")
            or not url.host
            or url.userinfo
            or url.query
            or url.fragment
        ):
            raise ValueError
    except (httpx.InvalidURL, ValueError) as exc:
        raise ValueError(
            "QWEN_VPS_URL must be an HTTP address without credentials or query parameters."
        ) from exc
    return value.rstrip("/")


def check_identity(model, name, digest):
    if name != model["tag"] or digest != model["digest"]:
        raise ValueError(
            "Qwen VPS returned a different model or digest. Check the pinned server model."
        )


def read_health(client, model):
    response = client.get("/health", timeout=5)
    response.raise_for_status()
    health = Health.model_validate(response.json())
    check_identity(model, health.model, health.digest)
    return health


def model_status(model):
    try:
        with httpx.Client(base_url=server_url(), trust_env=False, timeout=5) as client:
            health = read_health(client, model)
        return {
            "installed": True,
            "busy": health.busy,
            "availability_note": "Qwen VPS is busy; wait for its current request."
            if health.busy
            else "Qwen VPS is connected through the SSH tunnel.",
            "remote_digest": health.digest,
            "quantization": health.quantization,
        }
    except (httpx.HTTPError, ValidationError, json.JSONDecodeError, KeyError, TypeError):
        return {"installed": False, "availability_note": CONNECTION_HELP}
    except ValueError as exc:
        return {"installed": False, "availability_note": str(exc)}


def require_model(model):
    status = model_status(model)
    if not status["installed"] or status.get("busy"):
        raise ValueError(status["availability_note"])


def run(model, image_path, prompt, timeout_seconds):
    started = time.perf_counter()
    try:
        with httpx.Client(
            base_url=server_url(),
            timeout=httpx.Timeout(timeout_seconds, connect=5),
            trust_env=False,
        ) as client:
            health = read_health(client, model)
            if health.busy:
                raise ValueError("Qwen VPS is busy. Wait for its current request, then try again.")
            with image_path.open("rb") as image:
                response = client.post(
                    "/v1/analyze",
                    files={"file": (image_path.name, image, "application/octet-stream")},
                    data={"prompt": prompt, "max_tokens": "140"},
                )
            response.raise_for_status()
            answer = Answer.model_validate(response.json())
            check_identity(model, answer.model, answer.digest)
            if not answer.text.strip():
                raise ValueError("Qwen VPS returned an empty observation.")
    except httpx.TimeoutException as exc:
        raise ValueError(
            "Qwen VPS exceeded its time limit. Check the tunnel and server before retrying."
        ) from exc
    except httpx.HTTPStatusError as exc:
        messages = {
            429: "Qwen VPS is busy. Wait for its current request, then try again.",
            503: "The pinned Qwen model is not ready on the VPS. Check the server service.",
            504: "Qwen VPS exceeded its inference time limit.",
            422: "Qwen VPS rejected the image or prompt. Check the server input limits.",
        }
        raise ValueError(
            messages.get(
                exc.response.status_code,
                "Qwen VPS could not complete this request. Check its service log.",
            )
        ) from exc
    except httpx.HTTPError as exc:
        raise ValueError(CONNECTION_HELP) from exc
    except (ValidationError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(
            "Qwen VPS returned an invalid response; no observation was accepted."
        ) from exc
    data = answer.model_dump()
    gpu = answer.gpu_model_bytes
    device = "GPU" if gpu is not None and gpu > 0 else "CPU" if gpu == 0 else "device unreported"
    if gpu and answer.loaded_model_bytes and gpu < answer.loaded_model_bytes:
        device = "GPU + CPU"
    return {
        **data,
        "total_ms": round((time.perf_counter() - started) * 1000),
        "server_api_total_ms": answer.total_ms,
        "model_tag": answer.model,
        "model_digest": answer.digest,
        "runtime": "ollama",
        "runtime_version": f"ollama {answer.runtime_version}",
        "execution_target": "vps",
        "transport": "qwen-image-api-v1",
        "device": f"VPS · {device} · {health.quantization}",
        "quantization": health.quantization,
        "max_new_tokens": 140,
        "peak_rss_mb": None,
        "memory_note": "VPS allocation values are not peak-memory measurements. Peak RAM is unavailable.",
        "cache_policy": "Server keeps the model loaded for five minutes; model and prompt caches are not reset between runs.",
    }
