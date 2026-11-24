"""Check the private VPS image API without downloading or calling a real model.
These checks keep invalid images, missing models and failed inference visible to callers.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import asyncio
import base64
import io
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from deploy.qwen_vps import serve


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(serve, "inference_lock", asyncio.Lock())
    with TestClient(serve.app) as connection:
        yield connection


@pytest.fixture
def photo():
    output = io.BytesIO()
    Image.new("RGB", (1000, 600), "gray").save(output, "JPEG")
    return output.getvalue()


def runtime(monkeypatch, *, digest=None, answer=None, failure=None):
    calls = []

    def handler(request):
        if failure:
            raise failure
        if request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": serve.MODEL,
                            "digest": digest or serve.DIGEST,
                            "details": {"quantization_level": "Q4_K_M"},
                        }
                    ]
                },
            )
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "test-runtime"})
        if request.url.path == "/api/ps":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": serve.MODEL,
                            "size": 1234,
                            "size_vram": 1000,
                        }
                    ]
                },
            )
        assert request.url.path == "/api/chat"
        calls.append(json.loads(request.content))
        result = (
            answer
            if answer is not None
            else {
                "message": {"content": "A visible line.\nMore detail is unclear."},
                "done": True,
                "done_reason": "stop",
                "eval_count": 12,
                "prompt_eval_duration": 2_000_000,
            }
        )
        return httpx.Response(200, json=result)

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(
            **kw,
            transport=httpx.MockTransport(handler),
        ),
    )
    return calls


def test_health_requires_the_pinned_weights(monkeypatch, client):
    calls = runtime(monkeypatch, digest="different-weights")
    assert client.get("/health").status_code == 503
    assert not calls


def test_health_identifies_ready_runtime(monkeypatch, client):
    runtime(monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["runtime"] == "test-runtime"
    assert response.json()["quantization"] == "Q4_K_M"


def test_raw_answer_and_actual_image_reach_the_caller(monkeypatch, client, photo):
    calls = runtime(monkeypatch)
    response = client.post(
        "/v1/analyze",
        files={"file": ("wall.jpg", photo)},
        data={"prompt": "Describe what is visible.", "max_tokens": 80},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["text"] == "A visible line.\nMore detail is unclear."
    assert result["digest"] == serve.DIGEST
    assert result["runtime_version"] == "test-runtime"
    assert result["gpu_model_bytes"] == 1000
    assert result["prompt_eval_ms"] == 2
    sent = calls[0]["messages"][0]
    assert sent["content"] == "Describe what is visible."
    with Image.open(io.BytesIO(base64.b64decode(sent["images"][0]))) as image:
        assert image.size == (512, 307)
        assert image.format == "PNG"
    assert result["image_preprocessing"]["sent_dimensions"] == [512, 307]
    assert calls[0]["options"]["num_predict"] == 80


@pytest.mark.parametrize(
    "fields", [{"max_tokens": "513"}, {"max_tokens": "0"}, {"prompt": " "}, {"prompt": "x" * 6001}]
)
def test_invalid_options_never_call_qwen(monkeypatch, client, photo, fields):
    calls = runtime(monkeypatch)
    response = client.post("/v1/analyze", files={"file": ("wall.jpg", photo)}, data=fields)
    assert response.status_code == 422
    assert not calls


def test_invalid_file_is_rejected(monkeypatch, client):
    calls = runtime(monkeypatch)
    response = client.post("/v1/analyze", files={"file": ("wall.jpg", b"not an image")})
    assert response.status_code == 422
    assert not calls


def test_large_request_is_rejected_before_parsing(client):
    response = client.post(
        "/v1/analyze",
        content=b"small body",
        headers={"Content-Length": str(serve.MAX_BYTES + 200_000)},
    )
    assert response.status_code == 413


def test_missing_length_is_rejected(client):
    request = client.build_request("POST", "/v1/analyze", content=b"body")
    del request.headers["content-length"]
    assert client.send(request).status_code == 411


def test_busy_service_does_not_queue_more_work(monkeypatch, client, photo):
    calls = runtime(monkeypatch)
    asyncio.run(serve.inference_lock.acquire())
    try:
        response = client.post("/v1/analyze", files={"file": ("wall.jpg", photo)})
    finally:
        serve.inference_lock.release()
    assert response.status_code == 429
    assert response.headers["retry-after"] == "5"
    assert not calls


@pytest.mark.parametrize(
    "answer",
    [
        {"done": False, "message": {"content": "Partial text"}},
        {"done": True, "message": {"content": ""}},
    ],
)
def test_incomplete_output_is_a_failure(monkeypatch, client, photo, answer):
    runtime(monkeypatch, answer=answer)
    response = client.post("/v1/analyze", files={"file": ("wall.jpg", photo)})
    assert response.status_code == 502
    assert not serve.inference_lock.locked()


@pytest.mark.parametrize(
    "failure, status",
    [
        (httpx.ConnectError("private upstream details"), 502),
        (httpx.ReadTimeout("private upstream details"), 504),
    ],
)
def test_runtime_errors_do_not_become_demo_answers(monkeypatch, client, photo, failure, status):
    runtime(monkeypatch, failure=failure)
    response = client.post("/v1/analyze", files={"file": ("wall.jpg", photo)})
    assert response.status_code == status
    assert "private upstream details" not in response.text
    assert "text" not in response.json()
    assert not serve.inference_lock.locked()
