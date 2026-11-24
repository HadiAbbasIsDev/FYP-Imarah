# Running Imarah locally

The prepared machine already has the frontend build, a project virtual environment and the downloaded local models. Start with:

```bash
cd /home/it-admin/FYP-Imarah
.venv/bin/python scripts/start.py
```

Open `http://127.0.0.1:8000`. The server serves both the interface and API. If the address already opens the app, a server is running and there is nothing else to start.

On the prepared laptop, this command also starts the project-local Qwen server when needed. Four local model choices are installed, with an additional Qwen 4B VPS choice available through the SSH tunnel. The [local Qwen guide](local-qwen.md) and [VPS guide](vps-qwen.md) explain their separate connections. Earlier benchmarks stay in place.

The trained crack detector is configured and tested on this machine. Follow the [YOLO connection guide](yolo-endpoint.md) when setting up its deployment key on another computer or changing the service.

## Fresh Linux setup

Use Node 22.12+ and Python 3.10+. Keep several GB free for dependencies and at least 1.6 GB for the two small checkpoints, plus working room. A fresh PyTorch installation needs additional storage.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r backend/requirements-ml.txt
python -m pip install -r backend/requirements-dev.txt
python -m playwright install chromium
python scripts/prepare_fixtures.py
python scripts/download_models.py
cd frontend
npm ci
npm run build
cd ..
python scripts/start.py
```

The tested machine uses CPU PyTorch `2.13.0+cpu`, Transformers `4.57.1`, and Python `3.10.12`. Its `.venv` uses `--system-site-packages` to reuse already-installed CPU/ML packages and save disk space. **That environment is not a clean-room dependency reproduction.** The setup above is the intended isolated installation; repeat the tests after installing on another computer. See the [test record](../evaluation/testing.md).

Those commands install the two small baselines. To add Qwen3-VL 2B/4B, follow the separate guide; their model files need about another 5.2 GB, plus the runtime archive and working room.

Do not install CUDA wheels on this laptop. The image-processing code uses Pillow. An existing torchvision image-extension warning on the prepared machine does not mean a GPU is being used; actual inference was tested with the installed stack.

## Everyday development

Use two terminals:

```bash
# Terminal 1, project root
.venv/bin/python -m uvicorn backend.app.main:app --reload --port 8000
```

```bash
# Terminal 2
cd frontend
npm run dev
```

Vite prints the development URL. Rebuild the frontend before demonstrating the single-server production view. Use one production API worker; multiple workers would each have their own queue and model processes.

The direct `uvicorn` command does not manage Ollama. For Qwen development, keep `python scripts/ollama_local.py serve` running in another terminal, or use an already-running project model server.

## Windows and macOS

The frontend and PWA are platform-independent. The Python launcher also uses portable paths. On Windows, activate `.venv\Scripts\activate` and run `python scripts/start.py`; on macOS/Linux, use `.venv/bin/python`. Windows does not provide the Unix resource API, so peak RSS is left unmeasured there. These operating systems have not been tested in this session.

## Phone use and installation

The local URL on your laptop is not reachable from a different phone. For a trusted LAN demonstration, set `IMARAH_HOST=0.0.0.0`, restart the server, and visit `http://<laptop-LAN-IP>:8000` from the same Wi-Fi. There is no app authentication yet, so expose it only on a trusted network.

Mobile browsers generally require a secure origin for PWA service workers and installation. `localhost` is special on the same device; an ordinary LAN HTTP address is not. Use an HTTPS development proxy for a full installation test on a real phone. Do not expose the unauthenticated API to the public internet. Camera-picker behaviour also needs a real-device check; browser emulation is not a camera test.

In a supported browser, use **Install app** when it appears or the browser's install/add-to-home-screen option. Once visited, the interface shell can open offline. API records, photos and model inference still require the server.

## Useful commands

```bash
# API tests: no model downloads or real inference
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q

# Browser checks; start the server first
.venv/bin/python scripts/browser_smoke.py

# Segmentation-only display checks; requires a saved live inspection with outlines
.venv/bin/python scripts/check_segmentation_display.py

# A real comparison; start the server and download both models first
.venv/bin/python scripts/run_benchmark.py --repeats 2

# Recreate the editable diagrams and their SVG previews
.venv/bin/python scripts/build_diagrams.py

# Export a completed benchmark as an SVG/PNG figure
.venv/bin/python scripts/plot_benchmark.py benchmarks/results/bench-<id>.json
```

## Common fixes

| Symptom | What to check |
| --- | --- |
| Port 8000 is already in use | Open the existing server, or set `IMARAH_PORT` in `.env` |
| No models in the selector | Run `scripts/download_models.py`; a completed folder has a `READY` file |
| Qwen Local stays unavailable | Check the local vision server and follow [Qwen setup](local-qwen.md); missing or changed model digests stay disabled |
| Qwen VPS stays unavailable | Keep the SSH tunnel open and check port 18084 `/health`; follow the [VPS guide](vps-qwen.md). The app never substitutes the local option |
| Model download is slow | Leave the resumable download running; do not start several copies for the same model |
| VLM timeout | Close other heavy apps; use 256M; inspect local server logs; adjust `VLM_TIMEOUT_SECONDS` only after checking the cause |
| Live detector unavailable | Add the deployment key in `.env`, restart, and follow the [YOLO connection guide](yolo-endpoint.md) |
| Updated frontend does not appear | Rebuild and reload; if needed remove the app's old service worker/site cache |
| Model lab shows an interrupted run | Read preserved rows and run a new experiment; interrupted results are not silently completed |

Runtime data lives in `data/`. Back up this folder if you need to keep inspection records. Benchmark results are separate in `benchmarks/results/`. Stop the server before manually moving the SQLite database and its WAL files.
