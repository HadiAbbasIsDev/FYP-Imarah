"""Verify the separate Qwen 4B VPS choice and keep the existing local choices intact.
Fake HTTP responses exercise disconnects and provenance without using the live server.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import copy

import httpx
import pytest
from fastapi import HTTPException

from backend.app import main
from backend.app.services import remote_qwen, vlm

MODEL = vlm.get_model("qwen3-vl-4b-vps")
READY = {
    "status": "ready",
    "model": MODEL["tag"],
    "digest": MODEL["digest"],
    "quantization": "Q4_K_M",
    "runtime": "0.20.0",
    "busy": False,
}
ANSWER = {
    "text": "A visible crack.\nIts cause is unclear.",
    "model": MODEL["tag"],
    "digest": MODEL["digest"],
    "runtime_version": "0.20.0",
    "total_ms": 2000,
    "server_total_ms": 1990,
    "load_ms": 100,
    "prompt_eval_ms": 300,
    "generation_ms": 1500,
    "input_tokens": 200,
    "output_tokens": 20,
    "done_reason": "stop",
    "options": {"num_thread": 8, "num_predict": 140},
    "image_preprocessing": {"sent_dimensions": [512, 288], "sent_png_sha256": "a" * 64},
    "loaded_model_bytes": 9000,
    "gpu_model_bytes": 9000,
}


@pytest.fixture
def photo(tmp_path):
    path = tmp_path / "wall.jpg"
    # The gateway handles image decoding; this test verifies unchanged file transport.
    path.write_bytes(b"original photo bytes")
    return path


def mock_server(monkeypatch, *, health=None, answer=None, error=None, post_status=200):
    monkeypatch.setenv("QWEN_VPS_URL", "http://127.0.0.1:18084")
    requests = []

    def handler(request):
        assert request.url.port == 18084
        requests.append(request)
        if error:
            raise error
        if request.url.path == "/health":
            return httpx.Response(200, json=READY if health is None else health)
        assert request.url.path == "/v1/analyze"
        return httpx.Response(post_status, json=ANSWER if answer is None else answer)

    original = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original(
            **kwargs,
            transport=httpx.MockTransport(handler),
        ),
    )
    return requests


def forbid_local(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("Qwen 4B must never reach local inference or local availability checks")

    monkeypatch.setattr(vlm, "run_local", unexpected)
    monkeypatch.setattr(vlm.ollama_runtime, "require_model", unexpected)
    monkeypatch.setattr(main, "require_model", unexpected)


def test_selected_qwen_uses_vps_with_detector_context_and_provenance(monkeypatch, photo):
    calls = mock_server(monkeypatch)
    forbid_local(monkeypatch)
    monkeypatch.delenv("QWEN_VPS_TIMEOUT_SECONDS", raising=False)
    main.runnable("qwen3-vl-4b-vps")
    result = vlm.run_vlm("qwen3-vl-4b-vps", photo, evidence={"boxes": [{"label": "crack"}]})
    posted = next(request for request in calls if request.method == "POST")
    assert b"original photo bytes" in posted.content
    assert b"Separate detector context" in posted.content
    assert result["text"] == ANSWER["text"]
    assert result["execution_target"] == "vps"
    assert result["revision"] == MODEL["digest"]
    assert result["runtime_version"] == "ollama 0.20.0"
    assert result["device"] == "VPS · GPU · Q4_K_M"
    assert result["timeout_seconds"] == 330
    assert result["peak_rss_mb"] is None
    assert result["server_api_total_ms"] == 2000
    assert result["image_preprocessing"] == ANSWER["image_preprocessing"]


def test_local_weights_do_not_make_a_disconnected_vps_available(monkeypatch, photo):
    mock_server(monkeypatch, error=httpx.ConnectError("tunnel closed"))
    monkeypatch.setattr(
        vlm.ollama_runtime,
        "read_catalog",
        lambda: (
            {
                MODEL["tag"]: {
                    "name": MODEL["tag"],
                    "digest": MODEL["digest"],
                }
            },
            None,
        ),
    )
    forbid_local(monkeypatch)
    model = next(item for item in vlm.available_models() if item["id"] == MODEL["id"])
    assert not model["installed"]
    assert model["execution_target"] == "vps"
    assert "SSH tunnel" in model["availability_note"]
    with pytest.raises(HTTPException) as failure:
        main.runnable(MODEL["id"])
    assert failure.value.status_code == 422
    with pytest.raises(ValueError, match="SSH tunnel"):
        vlm.run_vlm(MODEL["id"], photo)


@pytest.mark.parametrize("field", ["model", "digest"])
def test_wrong_health_identity_blocks_submission(monkeypatch, field):
    health = {**READY, field: "wrong-model"}
    mock_server(monkeypatch, health=health)
    with pytest.raises(HTTPException) as failure:
        main.runnable(MODEL["id"])
    assert failure.value.status_code == 422


def test_busy_health_does_not_submit_an_image(monkeypatch, photo):
    calls = mock_server(monkeypatch, health={**READY, "busy": True})
    with pytest.raises(ValueError, match="busy"):
        vlm.run_vlm(MODEL["id"], photo)
    assert all(request.method == "GET" for request in calls)


@pytest.mark.parametrize(
    "status,message",
    [(429, "busy"), (502, "could not complete"), (503, "not ready"), (504, "time limit")],
)
def test_upstream_errors_never_fall_back(monkeypatch, photo, status, message):
    mock_server(monkeypatch, post_status=status)
    forbid_local(monkeypatch)
    with pytest.raises(ValueError, match=message):
        vlm.run_vlm(MODEL["id"], photo)


@pytest.mark.parametrize(
    "changes", [{"digest": "wrong"}, {"text": " "}, {"total_ms": -1}, {"runtime_version": ""}]
)
def test_bad_answer_is_rejected(monkeypatch, photo, changes):
    mock_server(monkeypatch, answer={**ANSWER, **changes})
    forbid_local(monkeypatch)
    with pytest.raises(ValueError):
        vlm.run_vlm(MODEL["id"], photo)


def test_cpu_response_is_not_labelled_as_gpu(monkeypatch, photo):
    mock_server(monkeypatch, answer={**ANSWER, "gpu_model_bytes": 0})
    assert vlm.run_vlm(MODEL["id"], photo)["device"] == "VPS · CPU · Q4_K_M"


@pytest.mark.parametrize("model_id", ["qwen3-vl-2b", "qwen3-vl-4b"])
def test_local_qwen_options_keep_their_local_worker(monkeypatch, photo, model_id):
    calls = []
    monkeypatch.setattr(vlm.ollama_runtime, "require_model", lambda model: None)
    monkeypatch.setattr(
        vlm, "run_local", lambda model, *args: calls.append(model["id"]) or {"text": "local"}
    )
    monkeypatch.setattr(
        remote_qwen, "run", lambda *args: pytest.fail("Local selection must stay local")
    )
    result = vlm.run_vlm(model_id, photo)
    assert calls == [model_id] and result["execution_target"] == "local"


@pytest.mark.parametrize("value", ["0", "nan", "inf", "invalid"])
def test_remote_timeout_is_validated(monkeypatch, photo, value):
    monkeypatch.setenv("QWEN_VPS_TIMEOUT_SECONDS", value)
    with pytest.raises(ValueError, match="QWEN_VPS_TIMEOUT_SECONDS"):
        vlm.run_vlm(MODEL["id"], photo)


def test_partial_report_keeps_detector_evidence_after_tunnel_loss(tmp_path, monkeypatch):
    from backend.app import database
    from backend.app.services import jobs

    monkeypatch.setattr(database, "DATA", tmp_path)
    monkeypatch.setattr(jobs, "UPLOADS", tmp_path)
    database.initialize()
    item = {
        "id": "remote-failure",
        "model_id": MODEL["id"],
        "status": "queued",
        "created_at": database.now(),
        "mode": "live",
        "dimensions": {"width": 10, "height": 10},
    }
    database.save_inspection(item)
    database.create_job(item["id"], "inspection")
    detector = {
        "status": "live",
        "boxes": [
            {
                "label": "crack",
                "confidence": 0.8,
                "box": [1, 1, 5, 5],
                "polygon": [[1, 1], [5, 1], [3, 5]],
            }
        ],
    }
    monkeypatch.setattr(jobs, "detect", lambda *args: copy.deepcopy(detector))
    mock_server(monkeypatch, error=httpx.ConnectError("connection lost after submission"))
    forbid_local(monkeypatch)
    jobs.inspection_job(item["id"])
    saved = database.get_inspection(item["id"])
    assert saved["status"] == "partial"
    assert saved["detection"] == detector
    assert "SSH tunnel" in saved["error"]
    assert saved["report"]["observation_source"] == "Unavailable"
