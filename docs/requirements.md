# Requirements and acceptance criteria

The [proposal](<../FYP-I-project-proposal-2026-final (1).pdf>) is the source of scope. The September implementation is an early demonstration of Module 1 and a navigation foundation for all four modules.

## People using the system

The final proposal serves building owners, engineers/reviewers, site managers, contractors, building-control stakeholders, and urban planners. Phase 1 uses one local student workspace. Its team avatar and reviewer-name field are not authentication or verified identity.

## September requirements

| ID | Requirement | Acceptance check | Current position |
| --- | --- | --- | --- |
| FR-01 | Use one interface on desktop and mobile | Open the same routes at desktop and phone widths without page overflow | Implemented; browser checks |
| FR-02 | Submit a surface photograph with context | Upload/sample/camera input; saved name, optional location and notes | Upload/sample tested; camera picker needs a real phone |
| FR-03 | Reject invalid images | Bad bytes, unsupported formats, over 10 MB, over 20 MP rejected | Implemented; API tests |
| FR-04 | Call the trained crack detector | Validate boxes and available segmentation outlines in saved-image pixels; display the actual predictions | Verified with live inference, saved polygons, segmentation-only display and exports |
| FR-05 | Generate a local VLM observation | Actual selected photo produces saved raw model text and provenance | Real experiments recorded in the model lab |
| FR-06 | Keep review and original output separate | Save reviewer notes without replacing raw VLM output | Implemented; API/browser checks |
| FR-07 | Recover and export inspection records | History survives API calls/restart; JSON and print view available | Implemented; tests and browser checks |
| FR-08 | Compare models transparently | Same prompt/images/settings; persist timing, memory, hashes and raw text | Implemented; real results versioned |
| FR-09 | Demonstrate future modules honestly | Workforce, sensors and urban pages state their data is simulated | Implemented; browser checks |
| FR-10 | Explain project stages | Roadmap dates and responsibilities agree with the proposal | Implemented; source review |
| FR-11 | Keep long jobs out of the UI request | Request returns a job ID; progress is polled; CPU process has a timeout | Implemented; bounded local queue |
| FR-12 | Make demo and live evidence distinguishable | No fake boxes on uploads; no silent fallback from a failed detector | Implemented; API tests |

## Later modules

| Module | Required work from the proposal | What the current preview demonstrates |
| --- | --- | --- |
| Construction management | Workers, contractors, payroll records, insurance, material usage and progress reports | Sample tables and material/task summaries |
| Attendance and PPE | Human detection with a reliable attendance process; gear compliance | Fictional check-ins and helmet/vest labels |
| Monitoring | Small sensor prototype; structural/environmental readings; weather integration | Selectable simulated trends and interpretation notes |
| Urban analysis | Geographic area selection; satellite/geospatial processing; density and a justified risk method | Schematic area selection and fictional indicators |
| Roles and access | Appropriate views and permissions for different stakeholders | One local team workspace, with no login claim |

Human detection alone does not establish a person's identity or attendance. The later attendance design needs registration, consent, matching/correction rules and validation. The worker preview does not score a person's productivity from imagery.

## Quality requirements

- **Readable code:** simple routes, service functions and typed page data; comments explain purpose.
- **Traceable results:** original evidence, versions and raw output remain inspectable.
- **Reliable failure handling:** invalid input fails early; unavailable models and restarts are explicit.
- **Reproducibility:** lock frontend packages, pin local model revisions, save exact experiment settings.
- **Practical laptop use:** one inference worker; no model downloads during a request; check free disk before download.
- **Responsive interface:** keyboard-accessible inputs and navigation, mobile layout, visible errors and progress.
- **Local data boundaries:** settings and uploads stay out of Git; remote detector credentials stay on the server.

## Exclusions retained from the proposal

No structural certification, no replacement of a qualified engineer, no real payment processing, no city-wide sensor deployment, and no direct integration into government/private internal systems. The Phase 1 software also does not yet include calibrated crack-width measurement, production authentication, real weather or satellite processing.
