# API and detector contract

Interactive API documentation is at `/docs` on the running server. All application endpoints are under `/api`. This local prototype does not have authentication.

## Application routes

| Method and route | Purpose |
| --- | --- |
| `GET /api/health` | API status, version, pending jobs and detector configuration state |
| `GET /api/models` | Model shortlist and local installation flags |
| `GET /api/samples` | Labelled research/synthetic fixture manifest |
| `POST /api/inspections` | Submit exactly one sample or image; returns 202 and an ID |
| `GET /api/inspections` | Most recent 200 local records |
| `GET /api/inspections/{id}` | Photo context, result, provenance and report |
| `PATCH /api/inspections/{id}/review` | Save reviewer name and notes |
| `GET /api/inspections/{id}/export` | Download the full record as JSON |
| `GET /api/jobs/{id}` | Poll queued/running/finished job state |
| `POST /api/benchmarks` | Submit a bounded model/image comparison |
| `GET /api/benchmarks` | Stored experiments, newest first |
| `GET /api/benchmarks/{id}/export` | Download an experiment's raw JSON |
| `GET /api/demo` | Clearly labelled fictional future-module data |

## Create an inspection

Send `multipart/form-data`:

```text
title       required, 1–100 characters, not blank
location    optional, at most 160 characters
notes       optional, at most 2,000 characters
model_id    an installed model, e.g. smolvlm-256m
mode        demo or live
sample_id   a known sample ID, OR
file        a JPEG, PNG or WebP upload (choose exactly one input)
```

The photo must be at most 10 MB and 20 megapixels. The server decodes it, corrects EXIF orientation, removes metadata and stores an RGB JPEG with its longest edge no larger than 1,600 pixels. File paths are generated from IDs, not client filenames.

Live mode returns 409 if the detector is unconfigured. Invalid input returns 422. Missing records return 404. Three queued/running jobs fill the small local queue; another submission returns 429. An inference timeout is recorded on the job/report rather than leaving the browser request open.

## Generic trained YOLO endpoint

Set these in the root `.env`:

```dotenv
YOLO_PROVIDER=generic
YOLO_ENDPOINT=https://your-model-host.example/predict
YOLO_API_KEY=
```

The API sends a multipart `file` named `inspection.jpg`. If a key is configured, it sends `Authorization: Bearer <key>`. This adapter expects pixel bounding boxes referring to the submitted image, not normalized coordinates and not a separately resized 640-pixel canvas.

Example response contract — **illustrative, not a result from the team's model**:

```json
{
  "detections": [
    {"label": "crack", "confidence": 0.87, "bbox": [120, 80, 260, 390]}
  ]
}
```

Each box is `[x1, y1, x2, y2]` with finite coordinates inside the image. Confidence is a finite number from 0 to 1. An empty detection list is a valid model response, but it is not evidence that a building is safe.

The adapter also accepts an Ultralytics `box` object (`x1`, `y1`, `x2`, `y2`) in `results`, or `images[0].results`. It can normalize `predictions` with centre-based `x`, `y`, `width`, `height` fields. Unsupported data fails rather than being guessed.

## Ultralytics-hosted connection

With `YOLO_PROVIDER=ultralytics`, the adapter targets **Ultralytics Platform dedicated deployments**. Set `YOLO_ENDPOINT` to the full prediction URL ending in `/predict` and `YOLO_API_KEY` to the key bound to that deployment. Requests use `Authorization: Bearer <key>`, multipart `file`, `imgsz=640`, `conf=0.25`, `iou=0.7`, and `normalize=false` for pixel coordinates. The deployment already selects its model, so no `YOLO_MODEL_ID` is needed. The older HUB `x-api-key`/`model` request is not this service's contract.

On 20 September, the supplied deployment's `/health` returned 200 with one cached model. Its `/openapi.json` confirmed the request and response format; a keyless POST to `/predict` returned 401. After the key was supplied, real image requests returned 200 and a complete browser inspection succeeded. The model reports task `segment`, with `crack` as class 0. Its results include `box` and `segments`; the adapter now preserves both. See the [verified results](../evaluation/yolo-findings.md) and [connection guide](../guides/yolo-endpoint.md).

`detector_configured` means the required local settings are present; it does not claim that the key has been accepted. Ultralytics live requests stay disabled while the key is empty. A rejected key produces an explicit error without copying it into the report.

The contract matches the [official endpoint documentation](https://docs.ultralytics.com/platform/deploy/endpoints/). A locally exported Ultralytics `.pt` file still needs an additional adapter.

### Segmentation in saved inspection records

Ultralytics returns `segments: {"x": [...], "y": [...]}` in an individual detection. The adapter pairs those coordinates, in their original order, into an optional `polygon` field in `detection.boxes[]`. The existing array name is retained for older clients and reports:

```json
{
  "label": "crack",
  "confidence": 0.8,
  "box": [10, 20, 40, 50],
  "polygon": [[10, 20], [40, 20], [25, 50]]
}
```

This triangle illustrates the data shape; it is not a prediction. Coordinates must be finite and inside the submitted image, the x/y lists must have matching lengths, and a nonempty outline needs at least three distinct points. A missing/null outline or two empty lists leaves a box-only detection. Malformed nonempty outlines fail explicitly rather than being silently discarded. No point simplification, box-to-mask conversion or smoothing is applied.

Polygons survive SQLite persistence and JSON export. The UI draws only blue segmentation outlines and lets the reader hide or show them. It has no box-view selector or rectangle fallback. Regions without a saved outline are omitted from the overlay, with an explanation. Demo illustrations are not drawn. Box coordinates remain in the stored evidence and export for compatibility and VLM context. VLM prompts continue to use only labels, confidence and box coordinates so long outlines cannot overwhelm the text context. See the [segmentation guide](../guides/segmentation.md).

## Review and benchmark requests

```json
{"reviewer": "Your name", "notes": "What you verified, corrected or want checked next."}
```

```json
{
  "model_ids": ["smolvlm-256m", "smolvlm-500m"],
  "sample_ids": ["cfd-001", "cfd-003", "synthetic-intact", "synthetic-crack"],
  "repeats": 2
}
```

Benchmark limits: 1–3 models, 1–6 known samples and 1–3 repetitions. Duplicate IDs are removed. Jobs run sequentially and results are saved after each row. A failure row remains part of the experiment.

The optional `prompt_version` field selects `surface-observation-v1` (default) or `brief-caption-v2`. These are named, fixed prompts in the source; unknown profiles return 422. Both the exact text and profile are copied into each experiment. The interface exposes the two choices in Model lab.

Ollama model entries also include `availability_note`, and, when installed, `local_digest`, `quantization` and `download_bytes`. A stopped/old server, missing model or mismatched recorded digest returns `installed: false`. Submitting an unavailable Ollama model returns 422 before a job is queued. No model is pulled as a side effect of an API request.

Completed Ollama observations add `runtime`, `model_tag`, `model_digest`, `quantization`, `model_details`, `options`, `prompt_eval_ms`, `server_total_ms`, `input_tokens`, `done_reason` and image-preprocessing metadata. `revision` holds the exact manifest digest for these rows. `peak_rss_mb` is null because the HTTP client's memory does not represent the separate model process. Older Transformers records remain valid.

## Separate Qwen Local and VPS choices

`qwen3-vl-4b` remains the local choice. `qwen3-vl-4b-vps` calls the dedicated VPS image API through `QWEN_VPS_URL` (default `http://127.0.0.1:18084`). `/api/models` includes `execution_target: local | vps`; a remote entry also has `remote_digest`, `busy` and an availability note. `installed` means ready at that entry's execution target. Local weights do not make an unreachable VPS entry available.

Submitting an unavailable or busy VPS choice returns 422 before queuing. The model's health and pinned digest are checked again before its image request, and the answer's identity is validated before saving it. An upstream busy response, timeout or disconnected tunnel stays an error. After successful detector work, such a failure produces the existing partial-report state and retains segmentation evidence. There is no automatic route between the Local and VPS choices.

New VLM records include `execution_target`. VPS records also include `transport: qwen-image-api-v1`, `server_api_total_ms`, `loaded_model_bytes`, `gpu_model_bytes` and `cache_policy`, alongside the original raw text and model settings. `total_ms` measures the app-to-VPS request including health lookup and transfer; `server_api_total_ms` measures time inside the gateway. Allocation fields are not peak-memory measurements. Older rows without these new fields retain their original meaning and are not migrated or rewritten.
