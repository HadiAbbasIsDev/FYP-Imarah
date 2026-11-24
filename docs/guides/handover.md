# Handover for the Imarah team

The app opens at **http://127.0.0.1:8000** on the prepared laptop. If the server has stopped, run `.venv/bin/python scripts/start.py` from the project root. Read the [demo walkthrough](evaluation-demo.md) before presenting.

## Inputs that still need you

1. **Record the detector's training identity.** The supplied endpoint and key now work, including live segmentation outlines and a complete inspection. Preserve the training run/checkpoint version and dataset details so later endpoint changes are traceable. See the [verified findings](../evaluation/yolo-findings.md), [overlay controls](segmentation.md) and [connection guide](yolo-endpoint.md).
2. **Choose the evaluation dataset and reviewers.** The original comparison uses two road photos and two synthetic controls; a public interior-wall photo is a separate exploratory example. For building-health claims, agree a held-out building-image set, annotation rules, and expert review with the supervisor.
3. **Try the PWA on your actual phones.** Responsive Chromium tests cannot verify a phone camera, iOS install behaviour, or your campus Wi-Fi/HTTPS setup. The [setup guide](setup.md) explains LAN access and installation constraints.

The disk-space issue was resolved before the Qwen continuation. Its runtime and download procedure are in the [local Qwen guide](local-qwen.md); completed model runs are recorded in [findings](../evaluation/model-findings.md).

## Before a public deployment

The current app is a trusted, local student workspace. Authentication, role permissions, verified reviewer identity, durable background processing, backup/retention, and deployment configuration are future work. Do not interpret the avatar as a login system. These boundaries are documented in [architecture](../architecture/README.md).

## What was left ready

- Frontend build and a one-command Python launcher.
- A configured, authenticated YOLO deployment and live wall-photo reports with SmolVLM 256M and Qwen3-VL 4B, pending human review. Reports now display saved segmentation outlines. The [connection findings](../evaluation/yolo-findings.md) include the returned evidence, timings and model mistakes; the [restoration record](../evaluation/segmentation-restoration.json) explains how discarded outlines were recovered for three existing reports.
- Four downloaded local VLMs: SmolVLM 256M/500M and Qwen3-VL 2B/4B. Their versions or manifest digests are pinned; resumed downloads were checked against complete-file SHA-256. See the findings for the experiments actually completed, and Model lab for the original responses.
- A completed, unreviewed **Interior wall · Qwen3-VL 4B** inspection (`74fdaf7ed0e94b69`), plus a synthetic 2B inspection with an explicitly automated workflow-test review. The wall report preserves the photograph's credit in JSON and PDF.
- A phase log, requirements, architecture, API contract, setup and evaluation guides.
- Six editable draw.io diagrams and matching SVG previews.
- Behaviour tests and a browser smoke-check script; see the final [test record](../evaluation/testing.md).

The [continuation snapshot](../evaluation/continuation-checks.json) records 62 passed backend tests, the real 19-check Qwen browser workflow, the final 18-check interface pass, and all 62 completed benchmark rows. The latest [Qwen findings](../evaluation/qwen-findings.md) include a chart and the model mistakes worth showing to the jury.

The project has its own local Git repository so Git operations stay inside `FYP-Imarah`, rather than the unrelated repository detected in the parent home directory. No commit, push, remote publication or message to the supervisor/jury was made. Review and commit the files when the team is ready.
