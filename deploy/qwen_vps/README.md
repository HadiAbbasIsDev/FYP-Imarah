# Qwen3-VL 4B Instruct on the VPS

This folder contains the small image API and service configuration for the Qwen model selected from our September wall-photo experiments. It accepts a photograph and returns the model's original description. It does not run YOLO, draw segmentation, assess structural safety, or change the model's words into a verified engineering conclusion.

The deployed copy belongs at `/sdb-disk/AIML-Models/VLM-models/qwen3-vl-4b-instruct-q4_k_m/`. Model weights and logs live on the data disk; Python and Ollama live under `/opt/aiml` on the root filesystem. Only this Qwen model is installed in this service's model store.

## Model identity

| Setting | Value |
| --- | --- |
| Original model | Qwen/Qwen3-VL-4B-Instruct |
| Ollama tag | `qwen3-vl:4b-instruct` |
| Quantization | Q4_K_M |
| Tested runtime | Ollama 0.20.0, CUDA 12 backend |
| Pinned manifest SHA-256 | `ee4b975b58c17ce268cd19d40db35d5edc64603035d2ffc1fee1968eb0947f7b` |
| Download size | 3,295,636,231 bytes across model layers |
| Model licence | Apache-2.0; preserve the upstream licence in the downloaded layers |
| Image view | RGB PNG, longest edge 512 pixels, aspect ratio retained |
| Generation | Temperature 0, seed 42, context 4,096, default 140 output tokens |
| Work limit | One request at a time; eight CPU threads when needed; five-minute inference timeout |
| Idle behaviour | Keep the loaded model for five minutes, then release it |

See the original [Qwen model card](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct) and [Ollama model entry](https://ollama.com/library/qwen3-vl:4b-instruct). This is the same pinned model used in the laptop comparison. Different hardware and runtimes can still produce different text and timing.

The VPS has a Tesla P100 with driver 550.127.08. Ollama 0.34.2 rejected GPU use with this combination, and its CPU image request reached the five-minute limit. The installed **0.20.0** release includes native compute-6.0 CUDA kernels and successfully processed real images on this GPU. We kept the existing driver. This is an explicit compatibility pin, not a recommendation to install an arbitrary older release. Recheck image inference and GPU allocation before changing the runtime. The [0.20.0 build settings](https://github.com/ollama/ollama/blob/v0.20.0/CMakePresets.json) include native compute 6.0; the [0.34.2 compatibility check](https://github.com/ollama/ollama/blob/v0.34.2/discover/cuda_compat.go) explains its newer driver requirement.

The verified release archive is `/sdb-disk/AIML-Models/_downloads/ollama-linux-amd64-0.20.0.tar.zst`, from the [official release](https://github.com/ollama/ollama/releases/tag/v0.20.0). Its SHA-256 is `60865e897ebd0f1fd481df2428fbbaf708e776b7926a3a24a1bb5bd0dd83d546`. The executable and CPU/CUDA-12 libraries are installed under `/opt/aiml/ollama/0.20.0/`; CUDA-13, Vulkan and MLX libraries were excluded during extraction. API packages are installed in `/opt/aiml/venvs/qwen3-vl-4b-api/`.

## Files on the server

```text
qwen3-vl-4b-instruct-q4_k_m/
├── README.md                      # this explanation
├── PC-CONNECTION.md               # deployed copy of the PC guide
├── SERVER-ENVIRONMENT.md          # deployed copy of server/storage defaults
├── serve.py                       # accepts and validates image requests
├── requirements.txt               # API dependencies, pinned versions
├── aiml-qwen4-api.service          # the image API, loopback port 18084
├── aiml-qwen4-ollama.service       # the model engine, loopback port 11440
├── logrotate.conf                 # keep service logs bounded
├── models/
│   ├── registry.json              # one model entry copied from the project registry
│   └── ollama/
│       ├── blobs/                 # content-addressed weights, config and licence
│       └── manifests/             # maps the model name to verified blobs
├── scripts/
│   ├── download_ollama_models.py  # resume downloads and verify complete SHA-256 hashes
│   ├── connect_qwen_vps.py        # copy to a PC to open the private tunnel
│   └── call_remote_qwen.py        # example image client
├── verification/                 # actual setup measurements and package versions
├── logs/                         # rotated engine and API logs
└── .runtime/model-downloads/      # resumable download working area
```

Keep Ollama's blob names intact. Renaming a GGUF blob to a friendly filename breaks its manifest lookup; the parent folder already supplies the readable model name. Application records belong in `/sdb-disk/projects/<project-name>/`, outside this reusable model folder.

## API contract

The API listens on **127.0.0.1:18084 on the VPS**. Access it from a PC through SSH, using the [PC connection guide](../../docs/guides/vps-qwen.md) in the repository. No password or API token is embedded in these files. SSH supplies access control and encryption; the HTTP listener is not a public endpoint.

| Route | Use |
| --- | --- |
| `GET /health` | Check the installed model digest and runtime; reports whether inference is busy |
| `POST /v1/analyze` | Multipart image field `file`, optional `prompt`, optional `max_tokens` |
| `GET /docs` | Interactive API contract while the tunnel is open |

Send JPEG, PNG or WebP, at most 10 MiB and 20 megapixels. Prompts must contain 1–6,000 characters, and output-token limits must be 1–512. Normal multipart clients send the required Content-Length header automatically. Image validation and re-encoding happen on the server even when a client has already checked its file.

Successful JSON contains `text`, model name/digest, runtime version, generation settings, image hash/dimensions, measured timings, token counts and the runtime's reported CPU/GPU model allocation. These allocation values are not peak-memory measurements. The API retains no uploaded photographs or prompt history. The multipart parser can use a temporary file during an upload; it is closed after validation, and the service uses its own private temporary directory. The response contains no filename or original camera metadata.

Failures remain failures: 411 means a missing length header; 413 means an oversized request; 422 means invalid input; 429 means busy; 503 means the pinned model is missing or changed; 502 means inference failed; 504 means inference timed out. Do not silently substitute another model or demo output. A completed answer with `done_reason: length` reached the token cap and may be cut short; preserve that reason when displaying it.

## Service maintenance

Use these commands inside an authenticated server session:

```bash
sudo systemctl status aiml-qwen4-ollama aiml-qwen4-api --no-pager
curl -fsS http://127.0.0.1:18084/health
sudo tail -n 40 /sdb-disk/AIML-Models/VLM-models/qwen3-vl-4b-instruct-q4_k_m/logs/api.log
```

After an intentional code/configuration update, copy the changed unit into `/etc/systemd/system/`, run `sudo systemctl daemon-reload`, and restart the affected service. Coordinate a restart with callers first. Both units are enabled at boot and require the data mount. A service restart was tested; a complete VPS reboot is a separate operation.

The `aiml-qwen` system account cannot log in. It runs both services with restricted write paths. The engine has a 24 GiB RAM limit and at most eight CPU cores' worth of scheduling; the API has a 1 GiB limit and two cores' worth. These limits leave capacity for other projects but do not reserve or partition GPU memory. Check GPU use before adding another service. Logs rotate daily or when checked above 10 MiB, with seven compressed rotations. Runtime-generated identity state lives in `/run/aiml-qwen-ollama`, not in the repository or the persistent model store.

To check or resume model files, run from the model folder as its maintenance owner:

```bash
/opt/aiml/venvs/qwen3-vl-4b-api/bin/python scripts/download_ollama_models.py --models qwen3-vl-4b
```

The server's `models/registry.json` contains only Qwen 4B. The helper refuses changed upstream manifests and only activates a download after every layer hash matches. Do not run a second downloader for the same store at the same time.

Our original source files carry the Imarah.tech notice. Upstream model and runtime licences remain separate.
