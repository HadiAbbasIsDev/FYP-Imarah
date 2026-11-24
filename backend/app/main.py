"""Serve Imarah's PWA, inspection API and recorded local/VPS model comparisons.
Run from the project root: python -m uvicorn backend.app.main:app --port 8000
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json
import re
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import database as db
from .config import FIXTURES, MAX_UPLOAD, PROJECT, RESULTS, UPLOADS
from .services import remote_qwen
from .services.detector import configuration_error
from .services.images import clean_image
from .services.jobs import benchmark_job, executor, inspection_job, samples
from .services.ollama_runtime import require_model
from .services.vlm import available_models, get_model


@asynccontextmanager
async def lifespan(app):
    db.initialize()
    # A result file can also be left mid-run if the machine lost power.
    for path in RESULTS.glob("*.json"):
        result = json.loads(path.read_text())
        if result.get("status") == "running":
            result.update(
                status="interrupted",
                error="Server restarted. Completed rows have been preserved.",
            )
            path.write_text(json.dumps(result, indent=2))
    yield


app = FastAPI(title="Imarah.tech · Phase 1", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def response_headers(request, call_next):
    # Reject clearly oversized requests before multipart parsing can spool them to disk.
    length = request.headers.get("content-length", "")
    if request.url.path == "/api/inspections" and request.method == "POST":
        if length.isdigit() and int(length) > MAX_UPLOAD + 128 * 1024:
            return JSONResponse(
                {"detail": "This upload is too large. Choose an image below 10 MB."},
                status_code=413,
            )
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    if request.url.path.startswith(("/api/", "/uploads/")):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "phase": "September 2026 · Phase 1",
        "detector_configured": configuration_error() is None,
        "pending_jobs": db.pending_count(),
        "local_only": True,
    }


@app.get("/api/models")
def models():
    return available_models()


@app.get("/api/samples")
def sample_list():
    return [{**s, "url": f"/samples/{s['file']}"} for s in samples()]


@app.get("/api/inspections")
def inspections():
    return db.list_inspections()


def find_inspection(item_id):
    item = db.get_inspection(item_id)
    if not item:
        raise HTTPException(404, "Inspection not found.")
    return item


@app.get("/api/inspections/{item_id}")
def inspection(item_id: str):
    return find_inspection(item_id)


def queue_available():
    if db.pending_count() >= 3:
        raise HTTPException(
            429, "The local runner is busy. Please wait for a current task to finish."
        )


def runnable(model_id):
    try:
        model = get_model(model_id)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if model["runtime"] == "planned":
        raise HTTPException(422, "This model is planned and cannot run yet.")
    if model.get("execution_target") == "vps":
        try:
            remote_qwen.require_model(model)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
    elif model["runtime"] == "ollama":
        try:
            require_model(model)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
    if (
        model["runtime"] == "transformers"
        and not (PROJECT / "models" / model_id / "READY").exists()
    ):
        raise HTTPException(422, "This model is not installed. Run scripts/download_models.py.")


@app.post("/api/inspections", status_code=202)
async def create_inspection(
    title: str = Form(..., min_length=1, max_length=100),
    location: str = Form("", max_length=160),
    notes: str = Form("", max_length=2000),
    mode: Literal["demo", "live"] = Form("demo"),
    model_id: str = Form("smolvlm-256m"),
    sample_id: str = Form(""),
    file: UploadFile | None = File(None),
):
    queue_available()
    runnable(model_id)
    if not title.strip():
        raise HTTPException(422, "Give this inspection a name.")
    if mode == "live" and (error := configuration_error()):
        raise HTTPException(409, error)
    if bool(sample_id) == bool(file):
        raise HTTPException(422, "Choose exactly one photo: a sample or an uploaded image.")
    sample = next((s for s in samples() if s["id"] == sample_id), None)
    if sample_id and not sample:
        raise HTTPException(404, "Sample not found.")
    content = (
        (FIXTURES / sample["file"]).read_bytes() if sample else await file.read(MAX_UPLOAD + 1)
    )
    item_id = uuid.uuid4().hex[:16]
    destination = UPLOADS / f"{item_id}.jpg"
    try:
        dimensions = clean_image(content, destination)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    item = {
        "id": item_id,
        "created_at": db.now(),
        "title": title.strip(),
        "location": location.strip(),
        "notes": notes.strip(),
        "mode": mode,
        "model_id": model_id,
        "sample_id": sample_id or None,
        "sample_kind": sample["kind"] if sample else None,
        "image_attribution": {
            **sample["attribution"],
            "changes": "Inspection copy resized and re-encoded as JPEG; camera metadata removed.",
        }
        if sample and sample.get("attribution")
        else None,
        "status": "queued",
        "dimensions": dimensions,
        "image_url": f"/uploads/{item_id}.jpg",
        "detection": None,
        "vlm": None,
        "report": None,
    }
    db.save_inspection(item)
    db.create_job(item_id, "inspection")
    executor.submit(inspection_job, item_id)
    return item


class Review(BaseModel):
    reviewer: str = Field(min_length=1, max_length=80)
    notes: str = Field(min_length=1, max_length=2000)


@app.patch("/api/inspections/{item_id}/review")
def review(item_id: str, review: Review):
    item = find_inspection(item_id)
    if not item.get("report"):
        raise HTTPException(409, "Wait until the report is available.")
    if not review.reviewer.strip() or not review.notes.strip():
        raise HTTPException(422, "Reviewer name and review notes cannot be blank.")
    item["report"]["review"] = {
        "status": "reviewed",
        "reviewer": review.reviewer.strip(),
        "notes": review.notes.strip(),
        "reviewed_at": db.now(),
        "identity_verified": False,
    }
    db.save_inspection(item)
    return item


@app.get("/api/inspections/{item_id}/export")
def export_inspection(item_id: str):
    item = find_inspection(item_id)
    return JSONResponse(
        item,
        headers={
            "Content-Disposition": f'attachment; filename="imarah-inspection-{item["id"]}.json"'
        },
    )


class BenchmarkRequest(BaseModel):
    model_ids: list[str] = Field(min_length=1, max_length=3)
    sample_ids: list[str] = Field(min_length=1, max_length=6)
    repeats: int = Field(default=1, ge=1, le=3)
    prompt_version: Literal["surface-observation-v1", "brief-caption-v2"] = "surface-observation-v1"


@app.post("/api/benchmarks", status_code=202)
def create_benchmark(request: BenchmarkRequest):
    queue_available()
    model_ids = list(dict.fromkeys(request.model_ids))
    sample_ids = list(dict.fromkeys(request.sample_ids))
    for model_id in model_ids:
        runnable(model_id)
    allowed = {s["id"] for s in samples()}
    if not set(sample_ids) <= allowed:
        raise HTTPException(422, "A benchmark sample is not available.")
    job_id = "bench-" + uuid.uuid4().hex[:12]
    db.create_job(job_id, "benchmark")
    executor.submit(
        benchmark_job, job_id, model_ids, sample_ids, request.repeats, request.prompt_version
    )
    return db.get_job(job_id)


@app.get("/api/benchmarks")
def benchmarks():
    records = [json.loads(path.read_text()) for path in RESULTS.glob("*.json")]
    return sorted(records, key=lambda record: record["created_at"], reverse=True)


@app.get("/api/benchmarks/{job_id}/export")
def export_benchmark(job_id: str):
    if not re.fullmatch(r"bench-[a-f0-9]{12}", job_id):
        raise HTTPException(404, "Benchmark not found.")
    path = RESULTS / f"{job_id}.json"
    if not path.exists():
        raise HTTPException(404, "Benchmark not found.")
    return FileResponse(path, filename=f"imarah-{job_id}.json", media_type="application/json")


@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    item = db.get_job(job_id)
    if not item:
        raise HTTPException(404, "Job not found.")
    return item


@app.get("/api/demo")
def demo():
    return json.loads((PROJECT / "backend/app/demo.json").read_text())


app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")
app.mount("/samples", StaticFiles(directory=FIXTURES), name="samples")


@app.get("/{path:path}")
def frontend(path: str):
    if path.startswith("api/"):
        raise HTTPException(404, "API route not found.")
    folder = (PROJECT / "frontend/dist").resolve()
    candidate = (folder / path).resolve()
    if candidate.is_relative_to(folder) and candidate.is_file():
        return FileResponse(candidate)
    if "." in Path(path).name:
        raise HTTPException(404, "File not found.")
    index = folder / "index.html"
    if not index.exists():
        raise HTTPException(503, "Build the frontend first: cd frontend && npm run build")
    return FileResponse(index)
