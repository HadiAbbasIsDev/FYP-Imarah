# Imarah.tech — Project Progress

Updated: 20 September 2026 · Phase 1

This is a simple summary of what we have completed and what we plan to work on next.

## Current progress

1. We have built a working web app with a layout that adjusts to desktop and mobile screens.
2. Users can upload a building photo, run an inspection, and view the results.
3. We have connected our trained YOLO crack model. The app now shows the actual crack outlines only, without drawing boxes.
4. We have tested four local vision-language models: SmolVLM 256M and 500M, and Qwen3-VL 2B and 4B. These models describe what they see in a photo.
5. The Model lab shows saved model responses and processing times. We have recorded 62 local comparison runs; these do not yet prove model accuracy.
6. Inspection reports can be saved, reviewed, exported as JSON, and printed or saved as PDF. The model's original words stay separate from the reviewer's notes.
7. Qwen3-VL 4B is running on our VPS GPU. The website offers separate **Local** and **VPS** options, so we can choose where it runs. Model files are organized under `AIML-Models/VLM-models`, and `SLMs` is reserved for later. Earlier benchmarks are kept unchanged.
8. We have added preview screens for worker management, safety equipment, attendance, sensors, and future project stages. These currently use sample data.
9. Setup guides, phase notes, model findings, and editable draw.io diagrams are available in the repository.
10. The latest checks passed 120 backend tests and the frontend build. The remote Qwen service also worked after restarting it.

## Upcoming work

1. Test the Local and VPS options on more photographs and compare their response times under clearly recorded conditions.
2. Collect more real building photos, including cracked and intact surfaces, and prepare labelled examples for testing.
3. Compare model results on those photos using the same test conditions. Record mistakes as well as useful answers, and measure accuracy only when suitable labels are available.
4. Review the reports with our supervisor or a relevant expert, improve unclear wording in the app, and prepare the evaluation demonstration.
5. Add user accounts, access permissions, and support for more than one user before making the full app publicly available.
6. In later phases, develop the worker-management features and connect verified attendance, work, and safety-equipment data.
7. Connect real sensors and test how their readings can support building monitoring and alerts.
8. Develop the planned urban-analysis features and complete the final project evaluation and documentation.

For detailed work records, see the [Phase 1 note](Phase1.md) and [September phase log](../docs/phases/01-september-2026.md).
