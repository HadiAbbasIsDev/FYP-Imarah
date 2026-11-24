# First authenticated crack-detector checks

The hosted detector is connected to Imarah. On 20 September 2026, the supplied deployment key was accepted and the app completed a real wall-photo inspection with YOLO evidence and a local VLM. The key stays in the ignored `.env`; the saved research records contain no credentials.

## What the endpoint actually returns

The service reports one class, `crack` (class 0), and task `segment`. Its wall response contains bounding boxes, confidence values and segmentation outlines as paired `x`/`y` lists. The first inspection adapter discarded the outlines, causing the box-only view noticed by the team. It now preserves and displays only the actual outlines. The initial box-view option and fallback were subsequently removed at the team’s request. The full direct-test response is preserved in [yolo-live-check.json](yolo-live-check.json); the [segmentation guide](../guides/segmentation.md) explains the display and verification.

Requests use the submitted JPEG's pixel coordinates, `imgsz=640`, `conf=0.25`, `iou=0.7`, and `normalize=false`. The service reports Ultralytics `8.4.153` and CPU PyTorch `2.14.0+cpu`. These are reported service versions, not a checkpoint identity or proof of its training history.

## Two direct image checks

| Image | Submitted size | Result | Client request time |
| --- | --- | --- | --- |
| Public interior wall, by Almanta | 1,600 × 900 | Three overlapping `crack` regions; confidences 0.40772, 0.35768 and 0.32235 | 7.119 s |
| Synthetic intact surface | 512 × 384 | No detections | 1.190 s |

Both requests returned HTTP 200. Client timings include the upload, remote processing and response; they are not pure model inference times. The endpoint separately reported inference times of 537.56943 ms and 461.32506 ms respectively. Two calls do not establish typical latency, and we have not established why the first request took longer.

The wall boxes overlap around a visible crack and extend over surrounding wall/baseboard areas. Three regions do **not** mean three separate cracks. There are no ground-truth annotations for this wall image, so these results are not precision, recall, mAP or segmentation-quality measurements. The intact control is a generated texture, not evidence that the detector can rule out defects in real buildings.

The wall photograph is [Cracked wall 03.jpg](https://commons.wikimedia.org/wiki/File:Cracked_wall_03.jpg), by Almanta, licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The submitted copy was resized and re-encoded as JPEG; source and submitted-file hashes are in the raw check record.

## Through the app

The browser created **Live YOLO · interior wall · SmolVLM 256M**, inspection `7faf63605aee492e`. The detector took 1.371 s and the VLM took 13.364 s. Three validated boxes and the 1,600 × 900 coordinate space were included in the VLM's recorded prompt. The browser observed about 18.715 s from submission until the report rendered.

The app saved the live detector evidence, displayed the three boxes, toggled them correctly, exported matching JSON and produced a printable PDF with the photo credit. The report fits 390 px and 768 px widths and had zero violations in the selected automated accessibility rules. The [browser check record](yolo-live-browser.json) contains the actual output and timings. It remains pending human review.

The small VLM's answer is a clear failure case: it guessed metal or plastic, described a diagonal crack and suggested depth without evidence. It repeated itself and ended mid-sentence. A successful detector connection does not make the following VLM answer reliable. The raw output is preserved for discussion rather than rewritten into a plausible report.

We also completed **Live YOLO · interior wall · Qwen3-VL 4B**, inspection `ecd9672320f14d29`, using the same submitted JPEG and the same three returned boxes. YOLO took 1.440 s and Qwen took 130.379 s. Its answer describes the textured wall, a vertical crack, white baseboard and wood-grain floor, without claiming a cause or depth. This is a more useful description of this particular photo, not a general quality ranking. Its full output and runtime settings are in [the Qwen check](yolo-qwen-browser.json).

Seven follow-up checks verified the Qwen report's live evidence, matching image hash and boxes, detector context in its prompt, JSON export, desktop/mobile layout, accessibility and PDF credits. Both new reports remain pending human review. For the evaluation, open the Qwen report to demonstrate the connected flow, then the small-model report to discuss why generated text still needs review.

## What comes next

Keep this connection check separate from the 62 earlier VLM-only benchmark rows, which did not use detector context. A useful next evaluation needs a held-out set of building photographs, annotated cracks, agreed measures for boxes and segmentation, and human review of generated observations. Record the training/export version before claiming reproducible checkpoint-level results from a replaceable hosted endpoint.
