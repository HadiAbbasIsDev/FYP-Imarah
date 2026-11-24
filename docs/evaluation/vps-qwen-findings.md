# Qwen VPS setup checks — 20 September 2026

The remote Qwen image API is working on the Tesla P100. We called it from the project PC through SSH, then restarted both server services and called it again. The model and release archive passed complete SHA-256 verification. The server's model store contains only Qwen3-VL 4B Instruct Q4_K_M.

## What we measured

| Request | API time | Model load time | Condition |
| --- | ---: | ---: | --- |
| Interior wall | 9.988 s | 7.704 s | First request after starting the GPU runtime |
| Same interior wall | 2.085 s | 0.281 s | Model already loaded; repeated input can use cached work |
| Synthetic intact surface | 2.379 s | 0.269 s | Different image, model already loaded |
| Interior wall after service restart | 8.524 s | See raw record | Confirms the service recovered and loaded the model again |

API time is measured inside the server and excludes the PC's image upload and network delay. These four requests are setup checks, not a latency distribution or a multi-user load test. The runtime reported 9,274,798,976 bytes for its loaded GPU model allocation. That value includes its runtime allocation and must not be presented as measured peak VRAM or the model download size.

Qwen described a vertical crack and a textured wall in the real photograph. On the generated intact control, it reported no visible cracks. The original wording is preserved in [the request/response record](vps-qwen-check.json); these two images and unlabelled descriptions do not establish accuracy, structural safety or a quality ranking.

The wall image is *Cracked wall 03.jpg* by Almanta, CC BY-SA 4.0, from [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Cracked_wall_03.jpg). The intact image is an Imarah.tech synthetic control. Both were sent through the image API without creating a persistent server upload collection.

## The compatibility issue we resolved

The server has driver 550.127.08. Ollama 0.34.2 declined to use the P100 with that driver, and the CPU request ended with HTTP 504 at the configured 300-second limit. We kept that failed attempt in the evidence rather than recording a fabricated answer or ignoring it.

We installed the checksum-verified Ollama 0.20.0 release, whose CUDA build includes native P100 kernels. Real GPU image requests then succeeded without a driver change. The dedicated service pins this runtime. See [its build settings](https://github.com/ollama/ollama/blob/v0.20.0/CMakePresets.json) and [the newer runtime's driver check](https://github.com/ollama/ollama/blob/v0.34.2/discover/cuda_compat.go). The unused trial runtime and its archive were removed after verification; the selected archive remains on the data disk.

The laptop comparison used CPU execution, four threads and Ollama 0.34.2. This server uses a P100, eight CPU threads when needed and Ollama 0.20.0. Do not mix these records into one supposedly matched model benchmark. A future benchmark should explicitly control hardware, runtime, warm/cold state, prompt, image preprocessing and repetitions.

## Software and operating checks

The complete API suite passes **99 tests**, including 15 for upload validation, pinned model identity, raw-output preservation, busy requests and upstream failures. The frontend production build passes. No interface behaviour changed, so this task did not add another application browser run; the new diagram's SVG preview was checked visually.

Both systemd services are active and enabled at boot, and their actual inference listeners are on VPS loopback. Restart recovery and an invalid-image response were checked live. A complete server reboot and Windows/macOS clients were not tested. The exact hardware snapshot, model hashes, package inventory on the server and service limits are recorded alongside [the environment evidence](vps-qwen-environment.json).

At the end of these initial deployment checks, the endpoint and PC client were ready and the app still used local adapters. The subsequent [website integration check](vps-website-check.json) covers the separate Local and VPS choices now available in inspections and Model lab. Existing local benchmarks retain their IDs and contents. The VPS adapter preserves model identity and raw output and surfaces failures, using [the API contract](../../deploy/qwen_vps/README.md).
