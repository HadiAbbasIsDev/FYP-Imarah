# A five-minute evaluation walkthrough

Open the app before the evaluation and keep the API terminal running. Use the saved results for a predictable presentation, and start one live local-model run if time allows.

## 1. Explain the problem from the overview

“Imarah puts building inspection evidence and construction information in one place. Our proposal has four modules. This September version demonstrates the inspection journey and makes the later modules visible.”

The overview's inspection, report and benchmark counts come from actual local records. The future-module cards lead to labelled previews.

## 2. Show an existing inspection

Open **Inspections** and choose **Live YOLO · interior wall · Qwen3-VL 4B** for the connected detector example. It is an unreviewed draft from an attributed public photograph, with three overlapping model regions. Explain that these are detector predictions, not three confirmed separate cracks. The [YOLO findings](../evaluation/yolo-findings.md) record the connection checks and VLM limitations. The matching **Live YOLO · interior wall · SmolVLM 256M** report is a useful failure case for the generated description.

Under **Visual evidence**, blue outlines follow the returned segmentation contours. Use **Hide regions** to inspect the underlying photo. The outlines are the model's actual coordinates. The interface draws no bounding boxes, including when an outline is missing.

The earlier **Interior wall · Qwen3-VL 4B** report was created in demo mode before detector credentials were available. It intentionally retains its original VLM-only evidence; connecting the endpoint does not retroactively change old reports.

For the synthetic-image and saved-review workflow, open **Evaluation sample · synthetic wall**. Point out its synthetic label and **Detector not used** badge. Historical illustrative boxes remain in its exported record, but are not drawn over the image.

The local VLM observation is real generated text. Explain that a report keeps detector evidence, the model's words, standard application guidance and review notes separate. The prepared automated review demonstrates saving a note; it is not a structural engineer's assessment.

The [latest findings](../evaluation/qwen-findings.md) explain why 4B is useful to discuss on this wall photo and why it is still not a validated building-inspection model. Show the 2B wall response too: its unsupported structural suggestion is an important failure case.

Use **Export JSON** to show the underlying record. **Print report** opens the browser's print dialog; choose “Save as PDF” if you want a PDF file.

## 3. Run one image if time permits

Choose **New inspection**, select a sample, and use SmolVLM 256M for a quick CPU workflow demonstration. Qwen3-VL 2B and 4B are also installed; allow a few minutes for a larger-model run. The public interior-wall sample shows its photographer and licence. Select **Trained YOLO endpoint** to include the hosted detector; it requires internet access and the configured deployment. **Demo workflow** still skips that detector explicitly. The small VLM's live wall example contains incorrect claims, which are worth showing rather than treating as a reliable assessment.

Start analysis. The record appears immediately while the CPU works in the background. Open the model lab while it runs, then return to the inspection when the draft is ready. This makes the asynchronous flow visible without waiting silently in front of the jury.

The camera button uses the device's camera/file picker. Demonstrate camera capture on a real phone only after checking that device and connection before the evaluation.

## 4. Show the model lab

Pick the saved repeated comparison and select the same image for all three models. Explain what the model got right, what it missed, and whether it went beyond visible evidence. The earlier SmolVLM 256M/500M comparison and the shorter-prompt experiments remain separate entries. The image-set selector separates the original four examples from the exploratory building photograph.

“These timings are measured on this CPU. We preserve exact settings and outputs. The four-image set is a smoke test, so we are not claiming an accuracy score or a final model winner yet.”

Qwen3-VL 2B/4B now appear as available locally. Their Q4_K_M configuration differs from the float32 SmolVLM setup, and their internal image processing differs too. The memory dash for Qwen means its process peak was not measured. InternVL, SmolVLM2 and Qwen2.5-VL 7B remain later candidates. Explain the next plan for a proper held-out building-image study.

## 5. Connect the preview to the proposal

In **Site management**, filter workers needing a PPE follow-up, open a sample assessment, and switch to materials and records. Explain that attendance, PPE and progress values are currently fictional.

In **Building monitoring**, change the sensor. Explain the planned calibrated sensor → timestamped record → weather context → review flow.

In **Urban analysis**, change the example area. Explain that it is a schematic, not satellite processing or a validated risk model.

Finish on **Project roadmap** to show September's foundation, the October–December building-health target and the tentative FYP-II stages.

## Questions worth preparing for

| Jury question | Honest answer |
| --- | --- |
| Is this the trained crack detector running? | Yes, in the saved live YOLO reports and new inspections using the trained endpoint. The blue outlines are its segmentation predictions; bounding boxes are never drawn. Earlier demo reports remain labelled as such. |
| Which VLM is best? | We can compare actual outputs, timing and resource use. A final quality conclusion needs labelled building examples and expert review. |
| Can it tell whether a building is safe? | No. It records visible evidence and supports review; the proposal excludes replacing professional structural assessment. |
| Is the worker/sensor data live? | No. Those screens demonstrate planned interactions with clearly labelled simulated records. |
| Why a PWA? | The proposal calls for one codebase on web and mobile. The interface adapts to both and has an installable shell. |
| What are your software-engineering practices? | Typed API data, server validation, separate services, persisted records, explicit failures, tests, versioned experiments, and current documentation. |
