# Editable project diagrams

Open any `.drawio` file in [diagrams.net](https://app.diagrams.net/) using **File → Open from → Device**, or use the draw.io extension in VS Code. Every node and connector is editable. The paired SVG can be viewed directly in the repository.

| Diagram | Editable source | Preview |
| --- | --- | --- |
| Connected system | [draw.io](architecture/system-overview.drawio) | [SVG](architecture/system-overview.svg) |
| Local deployment | [draw.io](architecture/local-deployment.drawio) | [SVG](architecture/local-deployment.svg) |
| Private VPS Qwen API | [draw.io](architecture/vps-qwen.drawio) | [SVG](architecture/vps-qwen.svg) |
| Inspection journey | [draw.io](flows/inspection-flow.drawio) | [SVG](flows/inspection-flow.svg) |
| Model comparison | [draw.io](flows/benchmark-flow.drawio) | [SVG](flows/benchmark-flow.svg) |
| Phase 1 storage | [draw.io](data/phase1-data-model.drawio) | [SVG](data/phase1-data-model.svg) |
| Project stages | [draw.io](roadmap/project-stages.drawio) | [SVG](roadmap/project-stages.svg) |

The files were generated as native uncompressed draw.io XML by `scripts/build_diagrams.py`; they are not screenshots pasted into a diagram. SVG previews use the same nodes and a simple connector layout. diagrams.net may route its editable connectors differently.

If updating through the script, edit its node/edge definitions and run it again. If editing a `.drawio` file manually, export a fresh SVG from diagrams.net and do not run the generator unless you also transfer that layout back into the script.

The diagrams show one local API process, one background worker, the hosted YOLO segmentation service, separate Local and VPS model routes, and clearly separated future modules. The inspection flow records the saved crack outlines as part of its evidence. The VPS route uses the owner's SSH tunnel; choosing it never silently starts a local model.
