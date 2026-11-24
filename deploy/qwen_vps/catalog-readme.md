# AIML Models

Shared model assets for OISOL-Sandbox live here, on the large `/sdb-disk` volume. Keep each model in its own descriptive folder, with a README, pinned identity, serving code, logs and verification notes. Keep project-specific uploads, datasets and results in `/sdb-disk/projects/<project-name>/` or a named dataset/checkpoint directory.

```text
AIML-Models/
├── VLM-models/
│   └── qwen3-vl-4b-instruct-q4_k_m/
├── SLMs/                  # reserved; no SLM downloaded yet
└── _downloads/            # verified runtime release archives
```

Use lowercase descriptive names below the requested top-level folders. Include model family, size, variant and quantization where applicable. Never reuse a model folder for different weights without recording a new identity. Do not place credentials in these directories.

| Owner/service | Address | Purpose |
| --- | --- | --- |
| `aiml-qwen4-api` | VPS loopback `127.0.0.1:18084` | Shared Qwen image API; reach through SSH |
| `aiml-qwen4-ollama` | VPS loopback `127.0.0.1:11440` | Internal Qwen model engine |
| Existing unrelated service | Port 9835 | Reserved; leave its configuration alone |

New projects need their own service names, ports and data directories. Reuse the Qwen image API where the pinned model fits; do not copy several identical weight stores by default. It serves one request at a time and returns HTTP 429 when busy. That is a deliberate limit for this stage, not a multi-user job scheduler.

OS packages, Python environments, Docker software and runtime executables belong on `/`, with this deployment under `/opt/aiml`. Large model files, archives, datasets, checkpoints, outputs, logs and Docker data volumes belong on `/sdb-disk`. Check disk and GPU availability before adding new workloads. GPU memory is shared, not partitioned by the service's RAM/CPU limits.
