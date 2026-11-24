"""Process inspections and fair, repeatable model comparisons one at a time.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import hashlib
import json
import logging
import platform
import uuid
from concurrent.futures import ThreadPoolExecutor

from .. import database as db
from ..config import FIXTURES, RESULTS, UPLOADS
from .detector import detect
from .vlm import PROMPT_VERSION, PROMPTS, get_model, run_vlm

executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="imarah")
logger = logging.getLogger("imarah")


def samples():
    manifest = FIXTURES / "manifest.json"
    return json.loads(manifest.read_text()) if manifest.exists() else []


def safe_error(exc):
    if isinstance(exc, ValueError):
        return str(exc)
    logger.exception("Job failed")
    return "A service could not finish this request. Check the local server log, then try again."


def inspection_job(item_id):
    item = db.get_inspection(item_id)
    try:
        item["status"] = "running"
        db.save_inspection(item)
        db.update_job(item_id, "running", "Checking the image and detector evidence")
        sample = next((s for s in samples() if s["id"] == item.get("sample_id")), None)
        path = UPLOADS / f"{item_id}.jpg"
        detection = detect(path, item["dimensions"], item["mode"], sample)
        item["detection"] = detection
        db.save_inspection(item)
        target = "VPS" if get_model(item["model_id"]).get("execution_target") == "vps" else "local"
        db.update_job(
            item_id, "running", f"Reading the photo with the {target} vision-language model"
        )
        try:
            # Only live detections enter the prompt; illustrative boxes must not bias the VLM.
            evidence = None
            if detection["status"] == "live":
                evidence = {
                    "source": "YOLO detector; coordinates are saved-image pixels",
                    "image_width": item["dimensions"]["width"],
                    "image_height": item["dimensions"]["height"],
                    # Thousands of outline points belong in the report, not the text prompt.
                    "boxes": [
                        {key: box[key] for key in ("label", "confidence", "box")}
                        for box in detection["boxes"]
                    ],
                }
            item["vlm"] = run_vlm(item["model_id"], path, evidence)
            item["status"] = "complete"
        except Exception as exc:
            item.update(status="partial", error=safe_error(exc))
        item["report"] = {
            "title": "Visual inspection draft",
            "evidence_summary": f"{len(detection['boxes'])} detector regions returned."
            if detection["status"] == "live"
            else "The trained detector was not used. Any marked region is an illustration.",
            "observation": (item.get("vlm") or {}).get(
                "text", "No VLM observation is available for this run."
            ),
            "observation_source": "Unreviewed VLM output" if item.get("vlm") else "Unavailable",
            "next_steps": [
                "Review the original photograph and the model's description together.",
                "Record location, scale and a second photograph before drawing conclusions.",
                "Refer structural concerns to a qualified engineer for an on-site assessment.",
            ],
            "limitations": "A photograph cannot establish structural safety, crack depth, cause or a calibrated measurement. This draft is decision support, not a certification.",
            "review": {"status": "pending", "reviewer": "", "notes": ""},
        }
        db.save_inspection(item)
        db.update_job(
            item_id,
            item["status"],
            "Draft ready for review"
            if item["status"] == "complete"
            else "Detector evidence saved; VLM needs attention",
        )
    except Exception as exc:
        message = safe_error(exc)
        item.update(status="failed", error=message)
        db.save_inspection(item)
        db.update_job(item_id, "failed", message)


def benchmark_job(job_id, model_ids, sample_ids, repeats=1, prompt_version=PROMPT_VERSION):
    result = {
        "id": job_id,
        "created_at": db.now(),
        "status": "running",
        "purpose": "Exploratory model/service comparison; not a model-accuracy study",
        "prompt": PROMPTS[prompt_version],
        "prompt_version": prompt_version,
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "scope": "This is the app host. VPS hardware is separate; read each row's execution target and device.",
            "local_threads_per_worker": 4,
        },
        "conditions": "Same source images and prompt, no detector context; sequential requests, 140-token limit and greedy decoding / temperature zero. Local models use CPU, four threads and fresh model loads; OS file caches are not cleared. SmolVLM uses float32 and a single square 512px view. Qwen uses quantized weights and an aspect-preserving 512px thumbnail. The Qwen 4B VPS option runs through the VPS API: its model stays loaded for five minutes and caches are not reset, so warm requests can be faster. VPS total time includes the HTTP health check, upload and response; server timing and GPU allocation are also recorded. Hardware, runtime and caching differ: these are service configurations, not an architecture-only comparison. Read each row's execution_target, device, options and preprocessing. Ollama peak process memory is unavailable.",
        "repeats": repeats,
        "rows": [],
    }
    destination = RESULTS / f"{job_id}.json"

    def persist():
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(json.dumps(result, indent=2))
        temporary.replace(destination)

    try:
        total = len(model_ids) * len(sample_ids) * repeats
        db.update_job(job_id, "running", f"Starting {total} image/model runs")
        persist()
        for model_id in model_ids:
            for sample_id in sample_ids:
                sample = next(s for s in samples() if s["id"] == sample_id)
                path = FIXTURES / sample["file"]
                for repeat in range(repeats):
                    db.update_job(
                        job_id,
                        "running",
                        f"Run {len(result['rows']) + 1}/{total}: {model_id} · {sample['name']}",
                    )
                    row = {
                        "id": uuid.uuid4().hex[:12],
                        "sample_id": sample_id,
                        "sample_name": sample["name"],
                        "sample_kind": sample["kind"],
                        "image_attribution": sample.get("attribution"),
                        "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "model_id": model_id,
                        "execution_target": get_model(model_id).get("execution_target", "local"),
                        "repeat": repeat + 1,
                        "human_review": None,
                    }
                    try:
                        row.update(
                            run_vlm(model_id, path, prompt_version=prompt_version),
                            status="complete",
                        )
                    except Exception as exc:
                        row.update(status="failed", error=safe_error(exc))
                    result["rows"].append(row)
                    persist()
        failures = sum(row["status"] == "failed" for row in result["rows"])
        result["status"] = (
            "complete" if not failures else "partial" if failures < total else "failed"
        )
        persist()
        db.update_job(
            job_id,
            result["status"],
            f"Finished {total - failures}/{total} runs. Raw outputs saved.",
        )
    except Exception as exc:
        result.update(status="failed", error=safe_error(exc))
        persist()
        db.update_job(job_id, "failed", result["error"])
