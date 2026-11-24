# Connecting our trained crack detector

The supplied address is the base URL of an Ultralytics Platform deployment. Our app sends photos to the `/predict` route on that service. The model stays hosted there; there is no need to download its weights to connect this endpoint.

## What is already prepared

The local `.env` contains the supplied prediction URL, `YOLO_PROVIDER=ultralytics`, and the deployment key. The app has been restarted and authenticated inference works. `.env` is excluded from Git and is readable only by the local file owner on this Linux machine. The frontend never receives the key. The steps below explain setup on another machine or after changing the deployment.

We checked the service on 20 September 2026:

- `/health` returned HTTP 200, `status: healthy`, and `cached_models: 1`.
- `/openapi.json` described Bearer authentication, a multipart image, and pixel-box results inside `images[0].results`.
- A POST to `/predict` with no key returned HTTP 401. No photograph was uploaded during that check.

After the key was supplied, two authenticated requests returned HTTP 200: three `crack` regions on the wall photograph and none on the synthetic intact control. A browser inspection then completed the hosted detector → local VLM → saved report flow. The endpoint returns segmentation outlines as well as boxes; the app shows only blue outlines, with no box-view option or rectangle fallback. Read the [actual findings](../evaluation/yolo-findings.md) and [overlay controls](segmentation.md).

## Add the deployment key

1. Open **Ultralytics Platform → Deploy** and find the deployment with the URL you supplied.
2. In **Cards** view, open that deployment's **Code** tab. Workspace owners can see the bound key in the ready-to-use request example. Copy the key value after `Bearer`, without copying the word `Bearer`.
3. Open `.env` in the project root and fill in `YOLO_API_KEY`. Keep the key in this local file rather than a Markdown document, screenshot, frontend file or chat message.

The relevant settings should look like this; the value below is a placeholder:

```dotenv
YOLO_ENDPOINT=https://predict-6aae986000b252409d0eaa84-dproatj77a-uc.a.run.app/predict
YOLO_PROVIDER=ultralytics
YOLO_API_KEY=PASTE_THE_DEPLOYMENT_KEY_HERE
```

Use the key bound to **this deployment**, not a newly created unrelated key. Its prefix is shown in the deployment card footer. If you are a team member and cannot see the full value, the owning workspace's owner must provide that key privately. These steps follow the [official endpoint instructions](https://docs.ultralytics.com/platform/deploy/endpoints/).

## Try one real inspection

After saving `.env`, restart the app: stop its terminal with `Ctrl+C`, then run this from the project root:

```bash
.venv/bin/python scripts/start.py
```

If a background copy is already serving port 8000, stop that existing Imarah process first; starting a second copy will not reload its settings. The prepared background process ID is recorded in `.runtime/server.pid`. Environment variables set outside `.env` take priority over the file.

Open the app at `http://127.0.0.1:8000`, choose **New inspection**, select a wall photo and **Trained YOLO endpoint**, and use **SmolVLM 256M** for the first quick check. The photo is sent to your hosted detector, then the local VLM reads it with the returned detector context. Check the saved report's live detector result and boxes. An empty box list is a possible successful response, not proof of a safe surface.

If authentication is rejected, check that the key matches the deployment's prefix and restart after editing. The app stays in an explicit failure state rather than substituting illustrative boxes. A stopped deployment must be started in Platform before it can accept predictions.

The adapter uses the deployment defaults of `imgsz=640`, `conf=0.25`, and `iou=0.7`, and explicitly requests `normalize=false`. No model ID or extra Python ML package is needed for this hosted connection. Its returned segmentation outlines are supported; a local `.pt` adapter remains separate future work.
