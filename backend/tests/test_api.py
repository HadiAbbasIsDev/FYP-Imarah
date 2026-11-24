"""Test the real API boundaries using temporary storage and a fake model runner.
These tests check behaviour; real VLM measurements live in benchmarks/results.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import io
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app import database, main
from backend.app.services import jobs


@pytest.fixture
def client(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    results = tmp_path / "results"
    uploads.mkdir()
    results.mkdir()
    monkeypatch.setattr(database, "DATA", tmp_path)
    monkeypatch.setattr(main, "UPLOADS", uploads)
    monkeypatch.setattr(jobs, "UPLOADS", uploads)
    monkeypatch.setattr(main, "RESULTS", results)
    monkeypatch.setattr(jobs, "RESULTS", results)
    monkeypatch.delenv("YOLO_ENDPOINT", raising=False)
    monkeypatch.setenv("YOLO_PROVIDER", "generic")
    monkeypatch.delenv("YOLO_API_KEY", raising=False)
    monkeypatch.setattr(main, "runnable", lambda model_id: None)
    monkeypatch.setattr(main, "executor", SimpleNamespace(submit=lambda fn, *args: fn(*args)))
    monkeypatch.setattr(
        jobs,
        "run_vlm",
        lambda *args, **kwargs: {"text": "Test-only model response.", "model_id": args[0]},
    )
    with TestClient(main.app) as client:
        yield client


def photo():
    output = io.BytesIO()
    Image.new("RGB", (120, 80), "grey").save(output, "JPEG")
    return output.getvalue()


def create(client, **fields):
    data = {"title": "Staircase surface", "sample_id": "synthetic-crack", **fields}
    return client.post("/api/inspections", data=data)


def test_inspection_persists_evidence_review_and_export(client):
    response = create(client)
    assert response.status_code == 202
    item_id = response.json()["id"]
    item = client.get(f"/api/inspections/{item_id}").json()
    assert item["status"] == "complete"
    assert item["detection"]["status"] == "illustration"
    assert item["detection"]["boxes"][0]["confidence"] is None
    assert item["report"]["observation"] == "Test-only model response."
    review = client.patch(
        f"/api/inspections/{item_id}/review",
        json={
            "reviewer": "Student reviewer",
            "notes": "Synthetic image; workflow test only.",
        },
    )
    assert review.status_code == 200
    assert review.json()["report"]["review"]["identity_verified"] is False
    exported = client.get(f"/api/inspections/{item_id}/export")
    assert exported.json()["report"]["review"]["notes"].startswith("Synthetic")
    assert "attachment" in exported.headers["content-disposition"]
    assert client.get("/api/inspections").json()[0]["id"] == item_id
    assert client.get(f"/api/jobs/{item_id}").json()["status"] == "complete"


def test_uploaded_demo_photo_does_not_get_invented_detections(client):
    response = client.post(
        "/api/inspections",
        data={"title": "Uploaded wall"},
        files={"file": ("../../unsafe.jpg", photo(), "image/jpeg")},
    )
    assert response.status_code == 202
    item = client.get("/api/inspections/" + response.json()["id"]).json()
    assert item["detection"]["boxes"] == []
    assert item["dimensions"] == {"width": 120, "height": 80}
    assert "unsafe" not in item["image_url"]


def test_public_photo_credit_survives_inspection_and_export(client):
    response = create(client, sample_id="commons-wall-03")
    assert response.status_code == 202
    item_id = response.json()["id"]
    exported = client.get(f"/api/inspections/{item_id}/export").json()
    assert exported["image_attribution"]["author"] == "Almanta"
    assert exported["image_attribution"]["license"] == "CC BY-SA 4.0"
    assert "resized" in exported["image_attribution"]["changes"]
    assert exported["detection"]["boxes"] == []
    assert exported["detection"]["source"] == "No detector used"
    assert "No illustrative regions" in exported["detection"]["note"]
    assert max(exported["dimensions"].values()) == 1600


def test_live_detector_context_includes_its_coordinate_space(client, monkeypatch):
    monkeypatch.setenv("YOLO_ENDPOINT", "https://detector.example/predict")
    monkeypatch.setattr(
        jobs,
        "detect",
        lambda *args: {
            "status": "live",
            "source": "test detector",
            "boxes": [],
            "note": "test only",
        },
    )
    observed = {}

    def model(model_id, path, evidence):
        observed.update(evidence)
        return {"text": "Test-only observation."}

    monkeypatch.setattr(jobs, "run_vlm", model)
    item_id = create(client, mode="live").json()["id"]
    item = client.get(f"/api/inspections/{item_id}").json()
    assert observed["image_width"] == item["dimensions"]["width"]
    assert observed["image_height"] == item["dimensions"]["height"]
    assert observed["boxes"] == []  # Even zero detections are meaningful context.
    assert "saved-image pixels" in observed["source"]


def test_platform_key_is_required_before_queueing(client, monkeypatch):
    monkeypatch.setenv("YOLO_ENDPOINT", "https://detector.example/predict")
    monkeypatch.setenv("YOLO_PROVIDER", "ultralytics")
    assert client.get("/api/health").json()["detector_configured"] is False
    response = create(client, mode="live")
    assert response.status_code == 409
    assert "YOLO_API_KEY" in response.json()["detail"]
    assert client.get("/api/inspections").json() == []
    monkeypatch.setenv("YOLO_API_KEY", "test-only-key")
    assert client.get("/api/health").json()["detector_configured"] is True


def test_segmentation_survives_storage_export_but_not_the_vlm_text_prompt(client, monkeypatch):
    monkeypatch.setenv("YOLO_ENDPOINT", "https://detector.example/predict")
    region = {
        "label": "crack",
        "confidence": 0.8,
        "box": [10, 20, 40, 50],
        "polygon": [[10, 20], [40, 20], [25, 50]],
    }
    monkeypatch.setattr(
        jobs,
        "detect",
        lambda *args: {
            "status": "live",
            "source": "test detector",
            "boxes": [region],
            "note": "test only",
        },
    )
    observed = {}

    def model(model_id, path, evidence):
        observed.update(evidence)
        return {"text": "Test-only observation."}

    monkeypatch.setattr(jobs, "run_vlm", model)
    item_id = create(client, mode="live").json()["id"]
    exported = client.get(f"/api/inspections/{item_id}/export").json()
    assert exported["status"] == "complete"
    assert exported["detection"]["boxes"] == [region]
    assert observed["boxes"] == [{key: region[key] for key in ("label", "confidence", "box")}]
    assert "polygon" not in observed["boxes"][0]


@pytest.mark.parametrize("content", [b"not an image", b"<svg><script>alert(1)</script></svg>", b""])
def test_corrupt_images_are_rejected(client, content):
    result = client.post(
        "/api/inspections",
        data={"title": "Invalid"},
        files={"file": ("photo.jpg", content, "image/jpeg")},
    )
    assert result.status_code == 422
    assert client.get("/api/inspections").json() == []


def test_upload_limit(client):
    result = client.post(
        "/api/inspections",
        data={"title": "Too large"},
        files={"file": ("large.jpg", b"0" * (10 * 1024 * 1024 + 1), "image/jpeg")},
    )
    assert result.status_code == 422


def test_oversized_request_is_rejected_before_parsing(client):
    result = client.post(
        "/api/inspections", content=b"placeholder", headers={"content-length": "50000000"}
    )
    assert result.status_code == 413
    assert client.get("/api/inspections").json() == []


@pytest.mark.parametrize(
    "fields,code",
    [
        ({"mode": "live"}, 409),
        ({"sample_id": "../outside"}, 404),
        ({"title": "   "}, 422),
        ({"mode": "secret"}, 422),
        ({"sample_id": ""}, 422),
    ],
)
def test_invalid_form_does_not_create_a_record(client, fields, code):
    assert create(client, **fields).status_code == code
    assert client.get("/api/inspections").json() == []


def test_cannot_upload_and_select_sample_at_once(client):
    result = client.post(
        "/api/inspections",
        data={"title": "Ambiguous", "sample_id": "synthetic-crack"},
        files={"file": ("test.jpg", photo(), "image/jpeg")},
    )
    assert result.status_code == 422


def test_vlm_failure_keeps_detector_evidence(client, monkeypatch):
    def fail(*args):
        raise ValueError("Model timed out.")

    monkeypatch.setattr(jobs, "run_vlm", fail)
    item_id = create(client).json()["id"]
    item = client.get(f"/api/inspections/{item_id}").json()
    assert item["status"] == "partial"
    assert item["error"] == "Model timed out."
    assert item["detection"] and item["report"]
    assert item["vlm"] is None


def test_detector_failure_is_not_hidden_as_demo(client, monkeypatch):
    def fail(*args):
        raise ValueError("Detector response has invalid coordinates.")

    monkeypatch.setattr(jobs, "detect", fail)
    item_id = create(client).json()["id"]
    item = client.get(f"/api/inspections/{item_id}").json()
    assert item["status"] == "failed"
    assert item["report"] is None


def test_blank_review_rejected(client):
    item_id = create(client).json()["id"]
    assert (
        client.patch(
            f"/api/inspections/{item_id}/review", json={"reviewer": " ", "notes": " "}
        ).status_code
        == 422
    )


def test_benchmark_preserves_input_hash_and_raw_output(client):
    response = client.post(
        "/api/benchmarks",
        json={
            "model_ids": ["smolvlm-256m", "smolvlm-500m"],
            "sample_ids": ["synthetic-intact"],
            "repeats": 2,
        },
    )
    assert response.status_code == 202
    result = client.get("/api/benchmarks").json()[0]
    assert result["status"] == "complete"
    assert len(result["rows"]) == 4
    assert len({row["image_sha256"] for row in result["rows"]}) == 1
    assert all(row["text"] == "Test-only model response." for row in result["rows"])
    assert all(row["human_review"] is None for row in result["rows"])
    assert client.get(f"/api/benchmarks/{response.json()['id']}/export").status_code == 200


def test_benchmark_rejects_unknown_sample_and_excessive_repeats(client):
    assert (
        client.post(
            "/api/benchmarks", json={"model_ids": ["a"], "sample_ids": ["missing"]}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/benchmarks",
            json={"model_ids": ["a"], "sample_ids": ["synthetic-intact"], "repeats": 4},
        ).status_code
        == 422
    )


def test_prompt_profile_is_validated_and_saved(client):
    body = {
        "model_ids": ["smolvlm-256m"],
        "sample_ids": ["synthetic-intact"],
        "prompt_version": "brief-caption-v2",
    }
    assert client.post("/api/benchmarks", json=body).status_code == 202
    record = client.get("/api/benchmarks").json()[0]
    assert record["prompt_version"] == "brief-caption-v2"
    assert record["prompt"].startswith("Describe this image in two short sentences.")
    body["prompt_version"] = "unknown-profile"
    assert client.post("/api/benchmarks", json=body).status_code == 422


def test_queue_limit_and_missing_records(client, monkeypatch):
    monkeypatch.setattr(database, "pending_count", lambda: 3)
    assert create(client).status_code == 429
    for path in [
        "/api/unknown",
        "/api/jobs/missing",
        "/api/inspections/missing",
        "/api/benchmarks/not-a-benchmark/export",
        "/api/benchmarks/%2e%2e%2fsecrets/export",
    ]:
        assert client.get(path).status_code == 404


def test_recovery_marks_unfinished_work(client):
    database.create_job("interrupted", "inspection")
    database.save_inspection(
        {"id": "interrupted", "created_at": database.now(), "status": "running"}
    )
    database.initialize()
    assert database.get_job("interrupted")["status"] == "failed"
    assert database.get_inspection("interrupted")["status"] == "failed"


def test_private_record_responses_are_not_cached(client):
    result = client.get("/api/inspections")
    assert result.headers["cache-control"] == "no-store"
    assert result.headers["x-content-type-options"] == "nosniff"
