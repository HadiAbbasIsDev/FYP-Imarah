# Phase 1 test record

The goal of testing here is to protect the inspection workflow and expose its limits. A passing interface test is not evidence that a model's description is correct.

## Automated checks

| Check | Command | What it covers |
| --- | --- | --- |
| API behaviour | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q` | Validation, persistence, review/export, errors, queue limits, restart handling, detector formats and benchmark records |
| Frontend build | `cd frontend && npm run build` | TypeScript checks and production asset build |
| Python checks | `.venv/bin/python -m ruff check backend scripts` | Basic errors and import consistency |
| Desktop/mobile browser | `.venv/bin/python scripts/browser_smoke.py` | Eight routes, page widths, workforce/sensor/area interactions, drawer and offline shell |
| Real workflow | `.venv/bin/python scripts/browser_smoke.py --live --model qwen3-vl-2b` | Real local-model inference, report, review save, JSON download and PDF output; the default model is SmolVLM 256M |
| Accessibility | Included in browser script with local `axe-core` | Automated WCAG 2 A/AA and 2.1 AA rules on rendered desktop routes |
| Model comparison | `.venv/bin/python scripts/run_benchmark.py --repeats 2` | Actual local inference on fixed image/model pairs |
| Dependency check | `cd frontend && npm audit` | Advisories reported for the installed JavaScript dependency tree |

The API test suite substitutes a small fake model runner and uses temporary databases/result directories. It tests software behaviour, not model quality. These fake results are never written to the research notebook.

## Latest verified results

The follow-up request for **segmentation only** removed every rectangle-rendering path from inspection overlays, including the box-view selector, missing-outline fallback and demo illustrations. The API suite remains at **84 passing tests**, with Ruff and the production build passing. The new repeatable `.venv/bin/python scripts/check_segmentation_display.py` passed **10 checks** against current saved reports and browser-only legacy/mixed/empty/demo fixtures; print/mobile views, exact polygons, exports, cache replacement and selected accessibility rules were verified. The general browser suite also passed **18 checks**, with zero selected-rule violations. See [segmentation-only results](segmentation-only-check.json). No stored detector output, VLM result or reviewer note was changed during this display update.

The segmentation update passed **84 backend tests**, Ruff and the frontend production build. Fifteen new cases cover outline preservation, empty-mask fallback, invalid coordinates/list lengths, and persistence/export without sending long polygons to the VLM text prompt. **Ten focused browser checks** verified the actual stored outlines in three restored reports, switching/hiding overlays, JSON export, responsive image alignment, PDF generation, zero selected accessibility-rule violations and older/mixed record handling. A fresh authenticated inspection (`b9217a60769847da`) also completed with three polygons saved by the updated pipeline. The broader **18-check browser smoke test** passed again with zero selected accessibility-rule violations. See [segmentation checks](segmentation-check.json) and [restoration provenance](segmentation-restoration.json). The older run records below remain historical evidence.

The subsequent Ultralytics connection update passed **69 backend tests**, Ruff, the frontend production build, and **18 browser checks with zero accessibility-rule violations**. Seven added cases check Platform and generic request formats, rejected-key messages, and refusal to queue or send an image when the required key is missing. These adapter tests use a mock HTTP service. The real endpoint separately returned 200 for health and its API specification, and 401 for a keyless prediction request; see the historical [connection check](yolo-connection-check.json).

After the deployment key was supplied, **two real authenticated detector requests returned 200**, followed by a complete live YOLO/SmolVLM browser inspection. Six focused browser checks cover actual detector context in the prompt, the live label and overlay toggle, matching JSON export, photo attribution, PDF generation, mobile report widths and automated accessibility (zero selected-rule violations, zero console errors). No model output was substituted, and the draft remains pending human review. See [detector results](yolo-live-check.json), [browser evidence](yolo-live-browser.json), and the [human-readable findings](yolo-findings.md). These integration results are separate from the earlier VLM-only benchmark rows.

A second complete live inspection used **Qwen3-VL 4B** with the same image hash and detector boxes. Its saved report passed seven focused checks, including prompt context, matching JSON, both mobile widths, zero selected-rule accessibility violations, and credits in both live-report PDFs. The [Qwen check](yolo-qwen-browser.json) preserves its actual response, 130.379-second VLM time, and pending review state. The API suite was rerun after configuration and passed **69 tests**; Ruff and the frontend build also passed. No application source changes were needed after supplying the key.

The first build on 19 September 2026 passed 38 API tests and 17 browser checks including a real SmolVLM inspection/review/export. Its JavaScript dependency audit reported zero known vulnerabilities.

During the 19–20 September continuation, the API suite passed **62 tests**. New cases cover Ollama availability, changed digests, missing vision capability, broken response streams, local-launcher ownership, invalid runtime archives, photo attribution, resumable-download integrity and valid, bounded timeout settings. Ruff and the frontend production build passed.

The real **Qwen3-VL 2B browser pass completed 19 checks**, including inference, review save, JSON download and printable PDF, separate image-set selection, visible photo credit, all eight routes at 390/768 pixels and the offline shell. Its original record is [browser-live-qwen2.json](browser-live-qwen2.json). A final interface-only pass completed **18 checks**, including the four-installed-model selection limit. Both passes reported **zero violations across the eight desktop routes** for the selected axe rules. A [separate earlier check](model-selection-check.json) also verified the three-model limit. A separately rendered real SmolVLM wall report had no violations for those rules and retained its source/licence in the printed PDF.

An [intentional three-second startup timeout](qwen-cancellation.json) returned the expected model error in 3.053 seconds. The local server reported no loaded runner immediately afterward, and the next real Qwen browser inspection completed successfully. This checks one early cancellation point; it is not a claim to have exercised every possible cancellation stage. The ordinary per-run ceiling is now 300 seconds, and invalid or unbounded timeout settings are rejected.

The completed [4B wall-report check](qwen-wall-report-check.json) verified its pending human-review state, absence of invented detector boxes, JSON export, and printed PDF with the photographer, licence and image-conversion note. That rendered report had zero violations for the selected axe rules and no console errors. The same check confirmed distinct accessible names for all four model checkboxes.

`environment.json` records the tested package versions. `browser-results.json` is the latest interface-only browser record; screenshots and generated PDFs are local artifacts under `docs/evaluation/screenshots/` and are ignored by Git. Starlette emits a deprecation warning about its test client's `httpx` support; all behaviour checks passed. The project's network client remains `httpx`.

## Findings already fixed

- A VLM failure initially hit a null-result bug during report construction. Partial reports now retain detector evidence and an explicit error.
- Missing/invalid coordinates and non-finite confidence are rejected by the detector adapter.
- Uploaded demo photos are tested to ensure no illustrative boxes are fabricated for them.
- Mobile test selectors were corrected to wait for route data and target the actual accessible navigation; all route widths are checked after rendering.
- Small-text colours were adjusted after axe found contrast issues. The subsequent eight-route scan reported zero violations for the selected rules.
- Frontend router and Vite dependencies were updated after the dependency audit found advisories. The subsequent audit reported zero known vulnerabilities.
- The new live-model browser selector initially used an exact label match that included the select's option text. Its selector was corrected and the full real Qwen workflow passed.
- A benchmark CLI poll hit a brief connection refusal during an idle app restart after its experiment had completed. The saved results were intact. Polling now retries a bounded number of connection failures against the same job; it never repeats the submission.
- The final visual review found that zero-box research samples still carried a human-marked-region label. Empty demo results now say that no detector or illustrative regions were used, and their region toggle is hidden. Four prepared records received only this source/note correction, with their model outputs and timings preserved; the [correction record](demo-label-correction.json) lists the changes. The API suite, build and browser checks were rerun after the fix.

## What has not been verified

- The trained detector's accuracy, checkpoint/training provenance or mask-quality metrics. Authenticated predictions and segmentation-outline rendering now work; the returned class is `crack` (0). Displaying the returned polygons is not evidence of their accuracy or a calibrated physical measurement.
- Accuracy, calibration, crack dimensions, structural safety, or the proposed human quality rubric.
- The remaining shortlist candidates (SmolVLM2, InternVL and Qwen2.5-VL 7B), GPU inference or fine-tuning.
- A fresh-machine dependency installation; the prepared environment reuses existing CPU/ML packages.
- Safari/iOS, Android camera capture, a real installed mobile PWA, or public HTTPS deployment.
- Live worker tracking, PPE models, sensors, weather, satellite processing, or multi-user access controls.

An automated accessibility scan does not replace manual keyboard and assistive-technology testing. Current mobile checks verify layout and navigation in Chromium at 390 px and 768 px; they do not reproduce every real device.

The [first-build check summary](final-checks.json) preserves the original two-model, 27-row snapshot. Later model setup is recorded in [Qwen runtime provenance](qwen-runtime.json); experiment outcomes and their limits are in [model findings](model-findings.md).

The [continuation check summary](continuation-checks.json) records four installed models, seven completed experiments and 62 real benchmark rows. Input hashes and model revisions/digests match their saved sources. The final health check found an empty job queue and no loaded Ollama runner; the app and local model server were left available on the laptop.
