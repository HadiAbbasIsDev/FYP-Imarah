"""Keep the trained detector's boxes and crack outlines in saved-image coordinates.
The demo boxes are human-marked illustrations, never claimed as model predictions.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import math
import os
import time

import httpx


def configuration_error():
    """Explain missing settings before putting an inspection in the work queue."""
    if not os.getenv("YOLO_ENDPOINT", "").strip():
        return "YOLO endpoint is not configured. Add YOLO_ENDPOINT to .env."
    provider = os.getenv("YOLO_PROVIDER", "generic").strip()
    if provider not in ("generic", "ultralytics"):
        return "YOLO_PROVIDER must be generic or ultralytics."
    if provider == "ultralytics" and not os.getenv("YOLO_API_KEY", "").strip():
        return "Add this Ultralytics deployment's API key to YOLO_API_KEY in .env, then restart the app."
    return None


def normalize_polygon(segments, width, height):
    """Pair Ultralytics x/y lists without changing or smoothing the predicted outline."""
    if segments is None:
        return None
    if not isinstance(segments, dict):
        raise ValueError("Detector segmentation must contain x and y coordinate lists.")
    xs, ys = segments.get("x"), segments.get("y")
    if not isinstance(xs, list) or not isinstance(ys, list) or len(xs) != len(ys):
        raise ValueError("Detector segmentation x and y lists must have matching lengths.")
    if not xs:
        return None  # Some services return an empty mask alongside a valid box.
    try:
        points = [[float(x), float(y)] for x, y in zip(xs, ys)]
    except (TypeError, ValueError) as exc:
        raise ValueError("Detector segmentation coordinates must be numbers.") from exc
    if any(not math.isfinite(v) for point in points for v in point):
        raise ValueError("Detector segmentation coordinates must be finite.")
    if any(not (0 <= x <= width and 0 <= y <= height) for x, y in points):
        raise ValueError("Detector segmentation must use pixels within the submitted image.")
    if len(set(map(tuple, points))) < 3:
        raise ValueError("Detector segmentation needs at least three distinct points.")
    return points


def normalize_detections(payload, width, height):
    # Support our documented contract, Ultralytics JSON and Roboflow-style JSON.
    if isinstance(payload, dict) and "images" in payload:
        images = payload["images"]
        if not isinstance(images, list) or not images:
            raise ValueError("Detector returned no image result.")
        payload = images[0]
    if isinstance(payload, dict):
        entries = next(
            (payload[k] for k in ("detections", "results", "predictions") if k in payload),
            None,
        )
    elif isinstance(payload, list):
        entries = payload
    else:
        entries = None
    if not isinstance(entries, list):
        raise ValueError(
            "Detector response must contain a detections, results or predictions list."
        )
    boxes = []
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("Invalid detection entry.")
        confidence = float(item.get("confidence", item.get("conf", -1)))
        if not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("Detector confidence must be between 0 and 1.")
        box = item.get("box", item.get("bbox"))
        if isinstance(box, dict):
            coordinates = [box[k] for k in ("x1", "y1", "x2", "y2")]
        elif isinstance(box, list) and len(box) == 4:
            coordinates = box
        elif all(k in item for k in ("x", "y", "width", "height")):
            x, y, w, h = [float(item[k]) for k in ("x", "y", "width", "height")]
            coordinates = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
        else:
            raise ValueError(
                "Detector returned a result without supported bounding-box coordinates."
            )
        x1, y1, x2, y2 = map(float, coordinates)
        if not all(math.isfinite(v) for v in (x1, y1, x2, y2)):
            raise ValueError("Detector coordinates must be finite.")
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            raise ValueError("Detector boxes must use pixels within the submitted image.")
        detection = {
            "label": str(item.get("name", item.get("label", item.get("class", "crack"))))[:80],
            "confidence": confidence,
            "box": [x1, y1, x2, y2],
        }
        polygon = normalize_polygon(item.get("segments"), width, height)
        if polygon is not None:
            detection["polygon"] = polygon
        boxes.append(detection)
    return boxes


def detect(path, dimensions, mode, sample=None):
    if mode == "demo":
        boxes = sample.get("demo_boxes", []) if sample else []
        return {
            "status": "illustration",
            "source": "Human-marked demo region" if boxes else "No detector used",
            "boxes": boxes,
            "latency_ms": None,
            "note": "The marked regions are human illustrations, not trained-detector predictions."
            if boxes
            else "The trained detector was not used. No illustrative regions were provided for this photograph.",
        }
    error = configuration_error()
    if error:
        raise ValueError(error)
    endpoint = os.environ["YOLO_ENDPOINT"].strip()
    headers = {}
    key = os.getenv("YOLO_API_KEY", "").strip()
    provider = os.getenv("YOLO_PROVIDER", "generic").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    data = {}
    if provider == "ultralytics":
        # Platform deployments already select the model. This is not the older HUB API.
        data = {
            "imgsz": "640",
            "conf": "0.25",
            "iou": "0.7",
            "normalize": "false",
        }
    started = time.perf_counter()
    with (
        open(path, "rb") as image,
        httpx.Client(timeout=float(os.getenv("YOLO_TIMEOUT_SECONDS", "45"))) as client,
    ):
        response = client.post(
            endpoint,
            files={"file": ("inspection.jpg", image, "image/jpeg")},
            data=data,
            headers=headers,
        )
        if response.status_code in (401, 403):
            raise ValueError(
                "YOLO endpoint rejected authentication. Check YOLO_API_KEY in .env; "
                "Ultralytics requires the key bound to this deployment. Restart after saving."
            )
        response.raise_for_status()
        boxes = normalize_detections(response.json(), dimensions["width"], dimensions["height"])
    return {
        "status": "live",
        "source": "Trained YOLO endpoint",
        "boxes": boxes,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "note": "Model detections are observations for review; confidence is not a structural risk score.",
    }
