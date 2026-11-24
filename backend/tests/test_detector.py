"""Check that supported endpoint responses are interpreted without guessing coordinates.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import httpx
import pytest

from backend.app.services import detector
from backend.app.services.detector import normalize_detections, normalize_polygon


@pytest.mark.parametrize(
    "payload",
    [
        {"detections": [{"label": "crack", "confidence": 0.8, "bbox": [10, 20, 40, 50]}]},
        {
            "images": [
                {
                    "results": [
                        {
                            "name": "crack",
                            "confidence": 0.8,
                            "box": {"x1": 10, "y1": 20, "x2": 40, "y2": 50},
                        }
                    ]
                }
            ]
        },
        {
            "predictions": [
                {
                    "class": "crack",
                    "confidence": 0.8,
                    "x": 25,
                    "y": 35,
                    "width": 30,
                    "height": 30,
                }
            ]
        },
    ],
)
def test_supported_formats_agree(payload):
    boxes = normalize_detections(payload, 100, 100)
    assert boxes == [{"label": "crack", "confidence": 0.8, "box": [10, 20, 40, 50]}]


@pytest.mark.parametrize(
    "payload",
    [
        {"unexpected": []},
        {"detections": [{"confidence": 0.8, "bbox": [50, 20, 10, 40]}]},
        {"detections": [{"confidence": 0.8, "bbox": [10, 20, 400, 50]}]},
        {"detections": [{"confidence": 3, "bbox": [10, 20, 40, 50]}]},
        {"detections": [{"confidence": float("nan"), "bbox": [10, 20, 40, 50]}]},
        {"detections": [{"confidence": 0.8, "bbox": [10, 20, float("inf"), 50]}]},
        {"detections": [{"confidence": 0.8}]},
        {"images": []},
    ],
)
def test_invalid_detections_are_rejected(payload):
    with pytest.raises(ValueError):
        normalize_detections(payload, 100, 100)


def test_empty_predictions_are_valid_and_are_not_safety_proof():
    assert normalize_detections({"detections": []}, 100, 100) == []


def test_segmentation_preserves_point_order_and_optional_closed_outline():
    segments = {"x": [10, 40, 25, 10], "y": [20, 20, 50, 20]}
    payload = {
        "results": [
            {
                "name": "crack",
                "confidence": 0.8,
                "box": {"x1": 10, "y1": 20, "x2": 40, "y2": 50},
                "segments": segments,
            }
        ]
    }
    result = normalize_detections(payload, 100, 100)[0]
    assert result["polygon"] == [[10, 20], [40, 20], [25, 50], [10, 20]]
    assert result["box"] == [10, 20, 40, 50]
    assert result["confidence"] == 0.8


@pytest.mark.parametrize("segments", [None, {"x": [], "y": []}])
def test_absent_or_empty_mask_keeps_a_box_without_inventing_a_polygon(segments):
    result = normalize_detections(
        {"detections": [{"confidence": 0.8, "bbox": [10, 20, 40, 50], "segments": segments}]},
        100,
        100,
    )[0]
    assert "polygon" not in result


@pytest.mark.parametrize(
    "segments",
    [
        [],
        {},
        {"x": [1, 2, 3], "y": [1, 2]},
        {"x": [1, 2], "y": [1, 2]},
        {"x": [1, 1, 1], "y": [2, 2, 2]},
        {"x": [1, 2, float("nan")], "y": [1, 2, 3]},
        {"x": [1, 2, 3], "y": [1, 2, float("inf")]},
        {"x": [-1, 2, 3], "y": [1, 2, 3]},
        {"x": [1, 2, 101], "y": [1, 2, 3]},
        {"x": [1, 2, 3], "y": [1, 2, 101]},
        {"x": [1, 2, "bad"], "y": [1, 2, 3]},
    ],
)
def test_invalid_segmentation_is_rejected_instead_of_hidden(segments):
    with pytest.raises(ValueError, match="segmentation"):
        normalize_polygon(segments, 100, 100)


@pytest.mark.parametrize(
    "provider,key", [("generic", ""), ("generic", "test-key"), ("ultralytics", "test-key")]
)
def test_request_matches_provider_contract(tmp_path, monkeypatch, provider, key):
    path = tmp_path / "image.jpg"
    path.write_bytes(b"test-image-bytes")
    monkeypatch.setenv("YOLO_ENDPOINT", "https://detector.example/predict")
    monkeypatch.setenv("YOLO_PROVIDER", provider)
    monkeypatch.setenv("YOLO_API_KEY", key)

    def respond(request):
        assert request.method == "POST"
        assert str(request.url) == "https://detector.example/predict"
        assert request.headers.get("Authorization") == (f"Bearer {key}" if key else None)
        assert "x-api-key" not in request.headers
        body = request.read().decode()
        assert 'name="file"; filename="inspection.jpg"' in body
        assert "test-image-bytes" in body
        if provider == "ultralytics":
            for field, value in {
                "imgsz": "640",
                "conf": "0.25",
                "iou": "0.7",
                "normalize": "false",
            }.items():
                assert f'name="{field}"\r\n\r\n{value}\r\n' in body
            assert 'name="model"' not in body
        return httpx.Response(200, json={"images": [{"shape": [100, 100], "results": []}]})

    client = httpx.Client(transport=httpx.MockTransport(respond))
    monkeypatch.setattr(detector.httpx, "Client", lambda **kwargs: client)
    result = detector.detect(path, {"width": 100, "height": 100}, "live")
    assert result["status"] == "live"
    assert result["boxes"] == []


@pytest.mark.parametrize("status", [401, 403])
def test_rejected_key_has_a_useful_error_without_leaking_it(tmp_path, monkeypatch, status):
    path = tmp_path / "image.jpg"
    path.write_bytes(b"test-image-bytes")
    monkeypatch.setenv("YOLO_ENDPOINT", "https://detector.example/predict")
    monkeypatch.setenv("YOLO_PROVIDER", "ultralytics")
    monkeypatch.setenv("YOLO_API_KEY", "private-test-key")
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status)))
    monkeypatch.setattr(detector.httpx, "Client", lambda **kwargs: client)
    with pytest.raises(ValueError, match="key bound to this deployment") as error:
        detector.detect(path, {"width": 100, "height": 100}, "live")
    assert "private-test-key" not in str(error.value)


def test_missing_platform_key_stops_before_reading_or_sending_image(monkeypatch):
    monkeypatch.setenv("YOLO_ENDPOINT", "https://detector.example/predict")
    monkeypatch.setenv("YOLO_PROVIDER", "ultralytics")
    monkeypatch.delenv("YOLO_API_KEY", raising=False)
    with pytest.raises(ValueError, match="YOLO_API_KEY"):
        detector.detect("does-not-exist.jpg", {"width": 100, "height": 100}, "live")
