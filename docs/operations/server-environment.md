# Default server environment

Use this DatabaseMart VPS as the project's default server when planning setup, deployments, storage or performance. The laptop remains a development and local-model environment. Credentials are deliberately absent from this document.

| Item | Configuration |
| --- | --- |
| Hostname | OISOL-Sandbox |
| Public address | 173.208.151.137 |
| Operating system | Ubuntu 22.04.2 LTS |
| CPU | Intel Xeon E5-2690 @ 2.90 GHz |
| CPU topology, verified | 2 sockets × 8 cores × 2 threads = 32 logical CPUs |
| RAM | 125 GiB |
| Swap | None |
| Root filesystem | 219 GB total; approximately 203 GB initially available |
| Data filesystem | `/sdb-disk`, 916 GB total; approximately 870 GB initially available |
| Boot partition | `/boot`, 1.7 GB as supplied by the owner |
| Network interface | eno1 as supplied by the owner |
| GPU, discovered during setup | NVIDIA Tesla P100 PCIe, 16 GiB VRAM |
| NVIDIA driver, observed | 550.127.08; `nvidia-smi` reports CUDA compatibility 12.4 |

Disk availability is a setup snapshot, not a permanent quota. Check it again before large transfers. The CPU has AVX but does not report AVX2. GPU/runtime compatibility needs an actual inference test; CPU thread count and RAM alone do not predict model latency.

## Tested Qwen deployment, 20 September 2026

Qwen3-VL 4B Instruct, Q4_K_M runs on the P100 through **Ollama 0.20.0**, with the existing driver unchanged. A real wall-image request through the PC's SSH tunnel completed in 9.988 seconds at the API, including 7.704 seconds of model loading. These are individual setup measurements, not a throughput or accuracy benchmark. The runtime reported the loaded model allocation on the GPU; see the [full verification record](../evaluation/vps-qwen-check.json).

The latest laptop runtime, 0.34.2, was unsuitable for this specific server/driver pairing: it declined the P100 and the CPU attempt timed out after 300 seconds. Pin 0.20.0 for this deployment until another runtime/driver combination is deliberately tested. Its [CUDA build configuration](https://github.com/ollama/ollama/blob/v0.20.0/CMakePresets.json) includes native compute-6.0 kernels. This is why copying a working laptop runtime onto another machine was not enough.

The image API is `127.0.0.1:18084` and the internal model engine is `127.0.0.1:11440`, both on VPS loopback. Service names are `aiml-qwen4-api` and `aiml-qwen4-ollama`. The [connection guide](../guides/vps-qwen.md) and [model-folder README](../../deploy/qwen_vps/README.md) cover normal use and maintenance. Future projects should reserve their own names and ports, and check the shared GPU before starting another workload.

In the website, `qwen3-vl-4b-vps` is the VPS choice and `qwen3-vl-4b` remains the original Local choice. Both use the same pinned weights but have separate runtime and timing records. Keep the SSH tunnel open for VPS calls; never silently redirect that choice to local inference. Old benchmark files remain unchanged.

## Storage rules

Use `/` for Ubuntu, system packages, NVIDIA/CUDA drivers, Python environments, Docker/system software and runtime binaries. This deployment reserves `/opt/aiml` for model-serving runtimes and virtual environments.

Use `/sdb-disk` for model files, Hugging Face caches, datasets, checkpoints, training outputs, large download archives, logs and large Docker volumes. Do not let a default cache silently fill `/` while the data disk has room.

```text
/sdb-disk/
├── AIML-Models/
│   ├── README.md
│   ├── VLM-models/
│   │   └── qwen3-vl-4b-instruct-q4_k_m/
│   ├── SLMs/
│   └── _downloads/
└── projects/
    └── imarah/
```

Only Qwen3-VL 4B Instruct is requested for the VPS at this stage. `SLMs` is reserved and should not trigger extra downloads. Share versioned model assets where practical; keep each project's images, records and experiments under its own project directory. Use lowercase descriptive names for individual model/project folders, with size and quantization in model names.

## Access and coexistence

The model service is intended to be called from the PC through an authenticated SSH tunnel. Keep inference listeners on server loopback; direct unauthenticated internet access is not required. Give new projects distinct ports, service names, data directories and resource limits. Existing service port 9835 was observed during setup and is not part of Imarah.

Do not record login passwords, private keys or API tokens in setup notes or files. The repository stores only non-secret configuration and observed results. Instructions in [AGENTS.md](../../AGENTS.md) point future work to this document.
