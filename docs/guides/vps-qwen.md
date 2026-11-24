# Calling Qwen on the VPS from your PC

The VPS hosts **Qwen3-VL 4B Instruct, Q4_K_M**, the same model that gave the useful wall description in our laptop experiments. The model files live at `/sdb-disk/AIML-Models/VLM-models/qwen3-vl-4b-instruct-q4_k_m/`. The other models stay on the development machine.

Real image inference was verified on its Tesla P100 with Ollama **0.20.0**. This runtime is pinned for compatibility with the existing GPU driver. The first wall request took 9.988 seconds at the API, including model loading; exact outputs and settings are in the [verification record](../evaluation/vps-qwen-check.json). This small setup check does not measure model accuracy.

## Connect and send a photo

From the project folder on the prepared Linux PC, open a terminal and run this, replacing `YOUR_SSH_USER` with your VPS login name:

```bash
.venv/bin/python scripts/connect_qwen_vps.py --user YOUR_SSH_USER
```

SSH asks for authentication. Type the password at its prompt; do not put it in the command, `.env`, source code or documentation. Keep this terminal open. It forwards your PC's `127.0.0.1:18084` to the private image API on the VPS. Closing it disconnects the PC; the VPS services keep running.

In a second terminal:

```bash
curl -fsS http://127.0.0.1:18084/health
.venv/bin/python scripts/call_remote_qwen.py --image benchmarks/fixtures/commons-wall-03.jpg
```

Replace the image path with your own JPEG, PNG or WebP. The sample wall photograph is by Almanta, CC BY-SA 4.0; its full credit is in [image sources](../../benchmarks/fixtures/SOURCES.md). The client prints JSON containing Qwen's unchanged text and actual model settings/timings. It does not save a local report automatically.

For a custom question:

```bash
.venv/bin/python scripts/call_remote_qwen.py --image path/to/photo.jpg \
  --prompt "Describe the visible cracks without guessing their cause." --max-tokens 140
```

Open [the interactive API page](http://127.0.0.1:18084/docs) while connected if you want to try uploads in the browser. This address is your PC's end of the tunnel. The VPS does not expose port 18084 to the internet.

On Windows, use an installed OpenSSH client and your environment's Python executable, for example `.venv\Scripts\python.exe`. On macOS, use its OpenSSH client and your Python environment. The scripts use ordinary Python and SSH, but this deployment was verified from the Linux project machine; Windows/macOS were not separately tested.

If local port 18084 is occupied, add `--local-port 18085` to the tunnel command and `--url http://127.0.0.1:18085` to the image client. A missing tunnel, failed SSH login or stopped VPS service is an error, not a reason to silently switch models.

## Connect another backend

Call the same multipart route from your backend. The `requests` example below assumes its own environment already has that package:

```python
# Send one photograph through an already-open SSH tunnel.
# Copyright (c) 2026 Imarah.tech. All rights reserved.
import requests

with open("image.jpg", "rb") as image:
    response = requests.post(
        "http://127.0.0.1:18084/v1/analyze",
        files={"file": image},
        data={"max_tokens": 140},
        timeout=330,
    )
response.raise_for_status()
result = response.json()
print(result["text"])
```

Keep detector evidence, raw VLM text and reviewer notes separate when integrating the response. Preserve its model digest, runtime version, preprocessing hash, settings and completion reason with any saved result. HTTP 429 means another request is running; show that state or retry later with a bounded policy. A 300-second server inference limit leaves some room inside the client's 330-second timeout for image transfer.

## Choose Local or VPS in the website

Keep the SSH terminal open and start the app in another terminal with `.venv/bin/python scripts/start.py`, or refresh the website if the app is already running. Both **New inspection** and **Model lab** offer these distinct choices:

| Website choice | Saved model ID | Where the image is processed |
| --- | --- | --- |
| Qwen3-VL · 4B · Local | `qwen3-vl-4b` | The existing local Ollama server on the PC |
| Qwen3-VL · 4B · VPS | `qwen3-vl-4b-vps` | The VPS image API through the SSH tunnel |

The local option keeps its existing ID, downloaded files and benchmark history. The VPS option has a separate ID and records the remote runtime, model digest, actual GPU/CPU allocation and request timing. Choosing VPS never falls back to local inference. If the tunnel drops, the selected option stays selected and becomes unavailable; a job that already saved YOLO results keeps them in a partial report.

`QWEN_VPS_URL` defaults to `http://127.0.0.1:18084`, and `QWEN_VPS_TIMEOUT_SECONDS` defaults to 330 seconds. For a different local tunnel port, change `QWEN_VPS_URL` in `.env` and restart the app. Keep `OLLAMA_URL` pointed at the local Ollama service: port 18084 serves a different API contract. No password belongs in either setting.

The server may keep the model warm for five minutes. Local Qwen runs unload between requests. New comparisons explain these different conditions, while all earlier benchmark files remain unchanged. Use each saved row's execution details when discussing results.

See [server defaults](../operations/server-environment.md), [model files and API contract](../../deploy/qwen_vps/README.md) and the [deployment diagram](../../diagrams/architecture/vps-qwen.svg). Loopback binding and a private tunnel follow [Ollama's server configuration](https://docs.ollama.com/faq); image generation uses its documented [chat API](https://docs.ollama.com/api/chat).
