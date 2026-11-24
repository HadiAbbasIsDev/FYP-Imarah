"""Check that unavailable or mismatched vision models cannot pretend to be ready.
Mock HTTP responses test failures; real model measurements live in benchmarks/results.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json

import httpx
import pytest
from fastapi import HTTPException
from PIL import Image

from backend.app import main
from backend.app.services import ollama_runtime
from scripts import ollama_worker

MODEL = {"id": "test-qwen", "runtime": "ollama", "tag": "test:vision", "digest": "sha256:recorded"}
INSTALLED = {
    "name": "test:vision",
    "digest": "sha256:recorded",
    "details": {"quantization_level": "Q4_K_M"},
}


def mock_http(monkeypatch, handler):
    original = httpx.Client
    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: original(**kwargs, transport=httpx.MockTransport(handler))
    )


@pytest.mark.parametrize("version", ["0.11.4", "unknown"])
def test_old_or_unknown_runtime_is_not_available(monkeypatch, version):
    mock_http(monkeypatch, lambda request: httpx.Response(200, json={"version": version}))
    catalog, error = ollama_runtime.read_catalog()
    assert not catalog
    assert "0.12.7" in error


def test_stopped_server_is_a_setup_state(monkeypatch):
    def offline(request):
        raise httpx.ConnectError("Server stopped")

    mock_http(monkeypatch, offline)
    catalog, error = ollama_runtime.read_catalog()
    assert not catalog
    assert "serve" in error


def test_malformed_optional_server_setting_does_not_break_model_discovery(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://127.0.0.1:invalid-port")
    catalog, error = ollama_runtime.read_catalog()
    assert not catalog and error


def test_missing_and_changed_tags_remain_disabled():
    assert not ollama_runtime.model_status(MODEL, {}, None)["installed"]
    changed = {"test:vision": {**INSTALLED, "digest": "sha256:changed"}}
    assert not ollama_runtime.model_status(MODEL, changed, None)["installed"]
    status = ollama_runtime.model_status(MODEL, {"test:vision": INSTALLED}, None)
    assert status["installed"]
    assert status["local_digest"] == "sha256:recorded"
    assert status["quantization"] == "Q4_K_M"


def test_api_rejects_unavailable_ollama_before_queuing(monkeypatch):
    monkeypatch.setattr(
        ollama_runtime, "read_catalog", lambda: ({}, "Start the local model server.")
    )
    with pytest.raises(HTTPException) as failure:
        main.runnable("qwen3-vl-2b")
    assert failure.value.status_code == 422
    assert "Start" in failure.value.detail


@pytest.fixture
def worker_request(tmp_path):
    path = tmp_path / "source.png"
    Image.new("RGB", (1000, 600), "gray").save(path)
    return {
        "model": MODEL,
        "ollama_url": "http://127.0.0.1:11435",
        "timeout_seconds": 180,
        "image_path": str(path),
        "prompt": "Visible details only.",
        "max_new_tokens": 140,
    }


def worker_server(monkeypatch, chunks, capabilities=None, digest=None):
    observed = []

    def handler(request):
        path = request.url.path
        if path == "/api/version":
            return httpx.Response(200, json={"version": "0.34.2"})
        if path == "/api/tags":
            return httpx.Response(
                200, json={"models": [{**INSTALLED, "digest": digest or INSTALLED["digest"]}]}
            )
        if path == "/api/show":
            return httpx.Response(
                200, json={"capabilities": ["vision"] if capabilities is None else capabilities}
            )
        if path == "/api/generate":
            assert json.loads(request.content)["keep_alive"] == 0
            return httpx.Response(200, json={"done": True})
        if path == "/api/ps":
            return httpx.Response(200, json={"models": []})
        assert path == "/api/chat"
        observed.append(json.loads(request.content))
        return httpx.Response(200, content="\n".join(json.dumps(chunk) for chunk in chunks))

    mock_http(monkeypatch, handler)
    return observed


def test_stream_preserves_raw_text_digest_and_runtime_settings(monkeypatch, worker_request):
    observed = worker_server(
        monkeypatch,
        [
            {"message": {"content": "A narrow "}},
            {"message": {"content": "line."}},
            {
                "done": True,
                "done_reason": "stop",
                "eval_count": 4,
                "load_duration": 1000000,
                "prompt_eval_duration": 2000000,
            },
        ],
    )
    result = ollama_worker.run(worker_request)
    assert result["text"] == "A narrow line."
    assert result["model_digest"] == MODEL["digest"]
    assert result["peak_rss_mb"] is None  # HTTP client memory is not model memory.
    assert result["image_preprocessing"]["sent_dimensions"] == [512, 307]
    assert result["prompt_eval_ms"] == 2
    assert result["runtime_version"] == "ollama 0.34.2"
    assert observed[0]["keep_alive"] == 0 and observed[0]["stream"]
    assert observed[0]["options"] == {
        "temperature": 0,
        "seed": 42,
        "num_predict": 140,
        "num_ctx": 4096,
        "num_thread": 4,
        "num_gpu": 0,
    }


@pytest.mark.parametrize(
    "chunks,message",
    [
        ([{"message": {"content": "Cut off"}}], "disconnected"),
        ([{"error": "Runner failed"}], "Runner failed"),
    ],
)
def test_incomplete_or_failed_stream_is_not_a_success(monkeypatch, worker_request, chunks, message):
    worker_server(monkeypatch, chunks)
    with pytest.raises(RuntimeError, match=message):
        ollama_worker.run(worker_request)


def test_text_only_model_never_receives_the_image(monkeypatch, worker_request):
    observed = worker_server(monkeypatch, [], capabilities=["completion"])
    with pytest.raises(RuntimeError, match="vision capability"):
        ollama_worker.run(worker_request)
    assert not observed


def test_model_changed_after_discovery_is_rejected(monkeypatch, worker_request):
    observed = worker_server(monkeypatch, [], digest="sha256:changed")
    with pytest.raises(RuntimeError, match="digest has changed"):
        ollama_worker.run(worker_request)
    assert not observed
