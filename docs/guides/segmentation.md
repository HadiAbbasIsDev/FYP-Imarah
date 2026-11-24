# Seeing the shape of a crack

Our trained model already returned segmentation. The first integration only kept its boxes, so Imarah drew rectangles while Ultralytics drew the crack's shape. We corrected that gap by preserving the returned outline coordinates and drawing them directly over the saved photograph.

## In the report

- Only saved **segmentation outlines** are drawn. Blue lines and a light blue fill follow the model's predicted contour. There is no box-view option.
- **Hide regions** shows the photograph without annotations; **Show regions** restores the segmentation.
- JSON exports retain the polygons. Printed reports use the currently visible overlay.

Older reports or box-only models can lack outlines. The app explains this and leaves the photo without an overlay; start a new live inspection to request segmentation. For mixed responses, only the available outlines are drawn and the missing ones are disclosed. Demo mode never draws an overlay, including old illustrative rectangles. Box coordinates remain in saved records and exports as detector evidence and concise VLM context; they are not rendered.

The lines represent the model's output, including mistakes. The app does not trace, smooth, or widen the crack. They are polygon contours returned by the service, not a calibrated width measurement or a separate dense pixel-mask export. A hosted model update, a different input resize, or different confidence/IoU settings can change a later prediction.

## Restoring the existing reports

Three successful live reports initially had only boxes saved. We backed up their full records before adding outlines:

- `89e03205542b45e1` (**Surface inspection**): replayed the detector on the exact saved JPEG. All six ordered boxes, labels and confidence values matched the original result, so the six returned polygons were attached.
- `ecd9672320f14d29` and `7faf63605aee492e`: recovered the three polygons from the preserved endpoint response after matching the saved-image hash, dimensions, ordered boxes and confidence values.

The [restoration record](../evaluation/segmentation-restoration.json) identifies those sources and comparisons. Each report also contains `detection.segmentation_restored` metadata. The original VLM words, prompts, timing measurements, field notes and review status were preserved. An older note describing the box-only display records the state at that earlier run; the restoration metadata explains the later addition. No failed or demo inspection was changed.

## Verification

The backend validates matching coordinate-list lengths, finite values, image bounds and at least three distinct points. Tests verify persistence/export and ensure polygon points do not flood the VLM text prompt; it continues receiving concise box context.

The earlier [browser check](../evaluation/segmentation-check.json) records the initial integration and a real new inspection. The current regression command is `.venv/bin/python scripts/check_segmentation_display.py`. It checks actual saved polygons, absence of rectangles and the old box selector, hide/show, exports, print/mobile views, accessibility, cache replacement, and legacy/mixed/empty/demo records. The result is saved in [segmentation-only checks](../evaluation/segmentation-only-check.json). Browser-only fixtures do not change the database or run YOLO.
