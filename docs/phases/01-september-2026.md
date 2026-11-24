# Phase 1: making the proposal demonstrable

**Period:** September 2026. **Implementation started:** 19 September 2026.

The proposal describes four connected modules. For the September evaluation, we needed something people could actually use, rather than a collection of disconnected diagrams. We brought the basic PWA and local VLM experiments forward, while leaving the proposal's full Module 1 evaluation in October–December.

## What we read

The eleven-page proposal defines a central PWA, building health assessment, construction site management, a small IoT monitoring prototype, and urbanization analysis. It also sets an important limit: the platform supports decisions and does not replace a qualified structural inspection. Payroll covers records, not payment processing.

The VLM DOCX lists Qwen3-VL 2B/4B, SmolVLM2 2.2B, InternVL2.5 4B, and Qwen2.5-VL 7B. The saved `Phase1.md` was empty, so the claimed trained-model endpoints and earlier flow were unavailable.

## What we built

The app has seven main areas: overview, inspections, model lab, site management, building monitoring, urban analysis, and project roadmap. Their visual style uses a restrained green palette and a simple building illustration. Desktop navigation becomes a drawer on mobile.

An inspection saves a cleaned copy of the image, queues analysis, and keeps the evidence in SQLite. Model inference runs in a child process so it can time out without freezing the API. There is one job worker to avoid loading several models at once on the laptop. A failed VLM leaves a partial report; a failed live detector never quietly becomes a demo result.

We made the research process visible. Each benchmark row includes its model revision, image hash, exact prompt, runtime settings, raw text, timing and worker memory. A reviewer can read two outputs next to the same photo. There is no invented accuracy percentage or automated structural-risk score.

The future screens cover the proposal's workforce, protective gear, attendance, work progress, salary records, insurance, materials, sensor context and area indicators. Those values are fictional and labelled on the page.

## Engineering and documentation

- TypeScript types describe API records; FastAPI validates inputs.
- Images are limited by byte size and dimensions, decoded with Pillow, re-encoded and stripped of camera metadata.
- Local uploads, database files, settings and model downloads are excluded from Git.
- Reports can be reviewed, exported as JSON and printed through the browser.
- Service-worker caching covers the interface, not uploaded photos or live API data.
- Seven native draw.io diagrams explain architecture, local and VPS deployment, inspection, benchmarking, storage and stages.
- Source files carry a basic use-case explanation and the requested Imarah.tech notice.

## Changes discovered during testing

The API failure tests caught a bug where an absent VLM result incorrectly turned a partial report into a total failure. That is fixed. Tests also verify that uploaded demo photos receive no invented boxes, that invalid coordinates are rejected, and that interrupted jobs show a restart message.

Real model runs exposed an avoidable CPU cost: the default image processor enlarged inputs to 2,048 pixels and created multiple tiles. We added an explicit single-view 512-pixel setting and recorded it as a separate experiment condition. One matched road image dropped from 55.291 seconds to 6.161 seconds in a diagnostic run. This changes visual detail and model output, so it is a practical prototype trade-off, not an accuracy improvement claim.

Detailed outcomes are in [testing](../evaluation/testing.md) and [model findings](../evaluation/model-findings.md). Keep those documents tied to actual test outputs, not estimated results.

## What still matters

The supplied YOLO deployment now works with authenticated images, segmentation outlines and the complete inspection flow. A proper building-image accuracy study remains future work. This is a local single-user prototype: app authentication, role permissions, durable multi-user job processing and deployment are later implementation work.

Real building photographs, a held-out evaluation set, annotation rules and expert feedback are needed before reporting crack-detection or report-quality metrics. The current road samples and synthetic controls only establish that the software runs and expose some model limitations.

## First-build research record

Both small VLMs are downloaded and tested. The notebook contains 27 completed model/image runs: three early tiled-processor runs, sixteen matched single-view runs, and eight shorter-prompt runs. The main comparison has a 10.269-second median for 256M and 14.967 seconds for 500M, with visible failure cases documented in the findings. Two prompt profiles are selectable and repeatable. No model-quality winner or trained-YOLO result is claimed.

## Continuation after freeing disk space

The team made about 23 GB available, allowing the original 2B and 4B Qwen shortlist to move forward. We installed a checksum-verified Ollama 0.34.2 copy inside the project, with CPU libraries and its own model store. The existing system installation was left in place.

The model adapter now checks server availability, version, tag digest and vision capability. It records actual quantization and processing settings with every answer, uses a bounded streaming request, and unloads models between runs. The model lab shows runtime-specific labels and treats an unmeasured memory value as unavailable.

We added an attributed public interior-wall photograph as a separate exploratory set. The original four-image sample selection remains available for reproducibility. New inspection records preserve the photograph's author, licence and conversion note through export. The deployment diagram now shows both local runtime paths.

Both Qwen model downloads passed their complete-file checksums. After native downloads repeatedly lost large unfinished sections, we added a small-range downloader with saved progress and final hash verification. This makes the setup easier to resume on the team's connection. A second invocation verified the completed layers without downloading them again.

The first 2B experiments showed why timing alone is not enough: it recognised the branching illustration that the small baselines missed, but a shorter prompt produced an unsupported depth claim on a road image. Image/prompt processing took most of the CPU time. We raised the per-image time limit from three to five minutes and kept the smaller model available for quick demonstrations.

The continuation passed 62 backend tests and a 19-check browser workflow with real Qwen inference, review and export. A separate browser check confirmed the three-model comparison limit with all four models installed. Detailed results remain in the test record so this phase note does not become a second, conflicting results table.

The continuation added 35 completed benchmark rows, bringing the notebook to 62 across four models. The three-model repeated comparison completed all 24 rows, followed by a separate three-model wall-photo comparison. On that wall example, 4B stayed closer to visible features, while 2B made an unsupported structural suggestion. Both the useful observations and failures are preserved in the [Qwen findings](../evaluation/qwen-findings.md).

The [Qwen decision note](../decisions/002-local-qwen.md) explains these choices. Completed experiment IDs, timings, observed errors and checks belong in the [model findings](../evaluation/model-findings.md) and [test record](../evaluation/testing.md).

## Connecting the supplied Ultralytics endpoint — 20 September

The team supplied its dedicated deployment URL. Its health route returned 200 with one cached model; its own OpenAPI specification confirmed `/predict`, Bearer authentication and pixel-box responses. A keyless prediction request returned 401, so no trained-model result is claimed yet.

We prepared the ignored local `.env` with that prediction URL and corrected the adapter's older HUB-style request to the Platform contract: a deployment key in the Bearer header, no model ID, and explicit pixel coordinates. The app checks that the key is present before queueing live work and gives a useful message if the service rejects it. The [connection guide](../guides/yolo-endpoint.md) explains where the owner can find the bound key and run the first authenticated inspection.

The team then supplied the key. Two authenticated requests succeeded: the public wall photograph returned three overlapping `crack` regions, and the intact synthetic control returned none. The service identifies its task as segmentation and returns both boxes and outlines. We preserved the full test response, although the first inspection adapter used only boxes. A real browser inspection completed with SmolVLM 256M, passed export/overlay/mobile/accessibility checks, and remains unreviewed. Its VLM output contains material and depth guesses, so this is useful integration evidence rather than a report-quality success. See [YOLO findings](../evaluation/yolo-findings.md).

A second connected inspection ran Qwen3-VL 4B on the identical submitted image and detector boxes. It described the wall's visible features more usefully and completed its VLM step in 130.379 seconds. The saved Qwen report also passed export, mobile, accessibility and PDF-credit checks. Both reports preserve their original outputs and still need human review; neither result has been added to the earlier VLM-only benchmark comparison. The final API checks remained at 69 passing tests, with Ruff and the frontend build passing.

## Showing the model's segmentation — 20 September

The team compared Imarah with Ultralytics and pointed out that our rectangles were losing the crack's shape. The model was already returning segmentation; our adapter discarded it. We now validate and save those original points, then draw blue outlines with a light fill over the photograph. The initial version let readers switch to boxes and used them when outlines were absent. That display choice was removed in the follow-up below; old records remain readable.

Three existing live reports received verified outline restorations. The team's uploaded **Surface inspection** was replayed against the detector on its saved JPEG; all six original ordered boxes, labels and confidence values matched, so we attached its six outlines. The two prepared wall reports used the previously preserved endpoint response with matching image hashes and boxes. Backups and [restoration provenance](../evaluation/segmentation-restoration.json) preserve what changed. VLM outputs, prompts, timings and reviews were not rewritten.

The updated pipeline also completed a new live wall inspection with three saved polygons. The suite passed **84 backend tests**, including invalid-outline rejection and storage/export checks, while ten focused browser checks verified exact points, display controls, responsive alignment, PDF output, accessibility and legacy/mixed responses. The draw.io architecture, inspection and data diagrams now include segmentation. See the [segmentation guide](../guides/segmentation.md) and [test evidence](../evaluation/segmentation-check.json).

## Removing all rectangle overlays

The team asked for segmentation only after rectangles appeared again. The latest saved reports already contained real polygons, but the interface still offered a box view and automatically drew boxes when an outline was absent. We removed both paths and the demo rectangle renderer. Reports now draw only returned polygons; missing outlines are explained without inventing or substituting a shape. Box coordinates remain in the saved evidence and VLM context, while the image overlay contains no rectangles.

The app-shell cache version was updated so activation clears the previous cached shell. The repeatable `scripts/check_segmentation_display.py` browser check covers actual latest reports plus browser-only legacy, mixed, empty and demo cases. It also checks print/mobile display, exports and cache replacement, without modifying stored inspection results.

## Dedicated Qwen service on the DatabaseMart VPS

The team supplied the server environment and asked to move only the successful Qwen candidate to it. We recorded the hardware/storage convention in [server defaults](../operations/server-environment.md) and AGENTS.md so later work keeps large assets off the root disk. The shared layout is `/sdb-disk/AIML-Models/{VLM-models,SLMs}`, with Qwen in `VLM-models/qwen3-vl-4b-instruct-q4_k_m/`. SLMs is only a reserved folder. Project records have their own `/sdb-disk/projects/<name>/` space.

We downloaded and verified the exact Qwen3-VL 4B Instruct Q4_K_M manifest and all model layers. The server also has a Tesla P100. The first runtime, Ollama 0.34.2, could not use its installed driver, and CPU inference reached the five-minute timeout. Ollama 0.20.0's native P100 kernels worked with the existing driver, so that version is pinned in a dedicated systemd service. Runtime binaries and a small Python environment live under `/opt/aiml`; weights, archives and rotated logs live on `/sdb-disk`.

A small FastAPI service validates photographs and returns Qwen's original answer, settings, image hash, model identity and measured timing. Both listeners bind to loopback. The PC reaches the image endpoint through SSH; the new tunnel and image-client scripts contain no password or API key. The service runs as a separate non-login account, accepts one inference at a time and has CPU/RAM limits to leave room for future projects. The model README explains the associated files and contract, and a paired draw.io/SVG diagram explains the connection.

The first GPU wall-image call completed in 9.988 seconds at the API, including model loading. See the [actual output record](../evaluation/vps-qwen-check.json), including the failed CPU attempt. This verified a working remote model service, not building-inspection accuracy. At this point the app still used its local adapters; the website integration followed below. This deployment passed **99 tests**, including 15 for the remote gateway, and the frontend production build. No interface behaviour changed in that deployment task.

## Choosing Local or VPS in the website

After the tunnel was confirmed working, the team asked to call Qwen from the website and keep both execution choices. We retained `qwen3-vl-4b` for the existing Local option and added `qwen3-vl-4b-vps` for the VPS option. Inspections and Model lab show the two choices separately. Existing benchmark files and local model weights remain unchanged.

The VPS adapter checks the remote model identity before sending an image, then validates the answer's identity and saves its raw text, runtime, preprocessing and measured timings. It never starts local inference. If the tunnel is unavailable, the website keeps the selected model and disables submission instead of silently picking a different one. A failure after YOLO completes preserves its segmentation in a partial report. Other local models keep their existing adapters.

New benchmark conditions explain that local models use fresh loads while the VPS may keep a warm model. Remote request time includes transfer, and reported GPU allocation is kept separate from peak-memory measurements. Earlier results are not relabelled or rewritten. The API suite passes **120 tests** and the frontend build passes. Browser verification is recorded in [the website connection check](../evaluation/vps-website-check.json).

The browser completed a real VPS image inspection and a separate VPS Model lab run, checked the saved/exported execution details, and confirmed that a simulated tunnel loss does not switch the selection to a local model. Both Local and VPS cards are visible. All seven earlier benchmark files passed before/after hash checks, and an earlier local comparison still renders with its CPU results. Ten segmentation regression checks passed against existing reports. A separate live-YOLO attempt failed because the laptop could not resolve the hosted detector's hostname; that failure remains saved. The successful VPS website test explicitly used detector-free mode, with real model inference.

## 27 September: PPIT startup assignment

Prepared three editable Word documents from the assignment brief: a memorandum of association, articles of association and business plan. The [assignment folder](../../PPIT-Assignment/README.md) contains the documents, source text and a rebuild script. The documents use the existing logo and the founders listed in the proposal. Proposed ownership, funding, roles and pricing are labelled as assumptions so that academic business planning is not mistaken for an incorporated company or actual sales.

The business plan covers all required sections A through K, separates the working inspection prototype from future modules, and includes sourced market context, quarterly cash flow, three-year projections and downside cases. Document XML, financial arithmetic and rendered page layout were checked. The final review copies have 4 pages for the memorandum, 5 for the articles and 11 for the business plan, including covers. Only assignment documents and their generator were added; application behaviour and model settings were not changed, so API and frontend tests were not rerun for this documentation task.

### Assignment budget correction

Revised all three assignment Word files and source text to match the team's contribution of PKR 15,000 per founder over one year, PKR 45,000 total. The proposed project spending is PKR 30,000 for low-cost equipment, PKR 9,000 for other costs and a PKR 6,000 reserve. Monthly instalments and the equipment breakdown remain explicit planning assumptions. Share subscriptions and the proposed capital figures were reconciled across the documents. The project-year cash flow is now separate from the later commercial scenario, which explicitly requires additional funding. Rechecked arithmetic and rendered layout; black-and-white styling and page counts are retained.
