# Working on Imarah.tech

This is a final year project. Favour readable, ordinary solutions that the team can defend and maintain.

- Read the proposal and the current phase note before expanding scope. Keep later modules visibly labelled until their data and models work.
- Explain the use case at the top of each source file in easy words, followed by `Copyright (c) 2026 Imarah.tech. All rights reserved.` Preserve third-party headers and licences.
- Keep functions focused. Prefer a small service module over a large framework or a new abstraction.
- Update the relevant phase log and documentation when behaviour, an API contract, a data structure or a model setting changes. Record why the change helps.
- Use TypeScript types at the browser/API boundary. Validate inputs in Python; the browser's validation is only a convenience.
- Keep detector results, raw VLM output, application guidance, and reviewer notes distinct. Do not invent prediction confidence, accuracy, risk scores, or benchmark results.
- Never silently replace a failed live model with demo data. Save a useful failure or partial report.
- Add meaningful tests for important behaviour. Run the API tests and frontend build after changes; run browser checks for interface changes.
- Store editable diagrams in the appropriate `diagrams/` subfolder and update their preview when the design changes.
- Keep model weights, uploads, databases, secrets and generated build folders out of Git. Do not remove unrelated files to make room for a model.
- The September server is a local, single-user prototype. Public deployment and real worker monitoring need their planned access controls and validation first.
- Do not publish, push, or contact anyone unless the user asks. Reversible local fixes and documentation updates are already within the working scope.

JSON data and strict configuration formats do not accept comments. Use their descriptive fields or the containing folder's README to explain their purpose; do not break the format just to add a header.

## Default server environment

- The project's default server is the DatabaseMart VPS **OISOL-Sandbox**, Ubuntu 22.04.2 LTS, at `173.208.151.137`. Consult `docs/operations/server-environment.md` before setup, storage, deployment or performance decisions.
- Keep system packages, drivers, runtimes and Python environments on `/`. Put large models, datasets, checkpoints, training outputs, logs and project data on `/sdb-disk`.
- Shared model assets belong under `/sdb-disk/AIML-Models/VLM-models/<model-name>` or `/sdb-disk/AIML-Models/SLMs/<model-name>`. Keep each project's operational data separate under `/sdb-disk/projects/<project-name>`.
- Never write passwords, private keys, API keys or other credentials into repository files, model READMEs, commands in documentation or logs. SSH authentication is entered interactively.
- This VPS may host several projects. Use distinct service names/ports and a README for each model; do not replace unrelated services or change drivers without first checking their dependencies.
