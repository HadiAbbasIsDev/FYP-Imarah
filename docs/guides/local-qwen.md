# Running the Qwen models locally

The September continuation adds the shortlisted Qwen3-VL 2B and 4B instruct models to the same inspection and model-lab workflow as SmolVLM. Downloading happens during setup. Reading a photograph uses the local files and does not start a download.

The website now also has a separate **Qwen3-VL · 4B · VPS** option, described in the [VPS guide](vps-qwen.md). The local 4B option keeps model ID `qwen3-vl-4b`; the VPS option uses `qwen3-vl-4b-vps`. This guide describes the Local choices. Existing local benchmarks remain unchanged.

## On the prepared Linux laptop

The project uses its own Ollama copy in `.runtime/ollama/` and model store in `models/ollama/`. Its address is `http://127.0.0.1:11435`. The older system installation and its existing models are separate.

After the local runtime is installed, the ordinary app command starts it automatically when needed:

```bash
.venv/bin/python scripts/start.py
```

The launcher stops only the model-server child that it started. If you already started a separate project model server, closing the app leaves that separate server running. The log is `.runtime/ollama.log`.

## Reproduce the setup

The Linux installer pins official Ollama **0.34.2** and checks the complete release archive against SHA-256 before extraction. It keeps the executable and CPU libraries in this repository's ignored runtime folder. It requires `curl`, `tar` and `zstd`; it does not run the system-wide installer.

```bash
.venv/bin/python scripts/ollama_local.py install

# Keep this terminal open during the downloads.
.venv/bin/python scripts/ollama_local.py serve
```

In a second terminal:

```bash
.venv/bin/python scripts/ollama_local.py pull qwen3-vl-2b
.venv/bin/python scripts/ollama_local.py pull qwen3-vl-4b
```

On this connection, long native downloads sometimes stalled and restarted large parts. The project also provides a downloader that saves completed 4 MiB ranges and resumes after an interruption:

```bash
.venv/bin/python scripts/download_ollama_models.py --models qwen3-vl-2b qwen3-vl-4b
```

Use one download method at a time for the same model. The resumable helper checks the pinned manifest before downloading, checks each response's byte range and size, and saves partial files under `.runtime/model-downloads/`. It verifies every complete layer by SHA-256 and registers the model only when all layers are complete. Repeating the command keeps completed pieces. A changed upstream tag or failed checksum stops activation; it never becomes a successful inference result.

The two instruct tags use Q4_K_M language weights. The registry records each installed manifest digest because a tag name alone can change upstream. If a fresh pull produces a different digest, the app keeps that model disabled until its provenance is reviewed and the registry is deliberately updated. Never edit a digest just to make an error disappear.

The official archive is around 1.43 GB; the normal Ollama model downloads are around 1.89 GB and 3.30 GB. Allow extra working room. The project keeps roughly 57 MB of CPU runtime files from that archive. A connection failure is not evidence that the model itself cannot run.

## Windows and macOS

The PWA/API remains cross-platform. The bundled archive installer is specifically for this Linux x86_64 laptop. On another operating system, install a compatible native Ollama build using its [official download instructions](https://ollama.com/download), start it with a project model folder and port 11435, then use the same model IDs and benchmark commands. Native Windows/macOS inference has not been tested in this session.

Alternatively, use a separately managed local Ollama instance and set `OLLAMA_URL` in `.env`, for example `http://127.0.0.1:11434`. Restart the API after changing the setting. The app will check that server; the launcher will not replace it. Downloads on a custom instance should use that instance's normal Ollama commands, since `ollama_local.py pull` intentionally targets the project port.

## What the app checks

Model discovery reads the server version and installed tags without sending a photograph. An old or stopped server, missing tag, or changed digest is shown as unavailable. Immediately before inference, the worker rechecks the digest and requires the model's `vision` capability.

Each Qwen request uses CPU execution, four threads, a 4,096-token context, temperature zero, seed 42 and up to 140 output tokens. An RGB image thumbnail preserves aspect ratio with a longest edge of 512 pixels. Ollama handles the model's native vision processing. These settings are saved with the output.

The worker unloads a previous copy before a timed run and requests unloading after completion. Its streaming connection closes if the outer Python timeout kills the worker. The default time limit is 300 seconds per image/model run. It was increased from 180 after the first 2B runs took 66–143 seconds with changing laptop load; the larger candidate needed reasonable headroom. The first 4B repetitions later took 178 and 183 seconds, confirming that the earlier ceiling was tight. Most of that elapsed time was image/prompt processing. `VLM_TIMEOUT_SECONDS` can be changed in `.env`; new successful rows record the actual configured limit. Older rows predate that field and used 180 seconds.

Ollama's API does not report a reliable peak resident-memory measurement for its model runner. The app therefore leaves that value blank. The memory of the small HTTP client would be a misleading substitute.

## Repeat a matched comparison

With the app running:

```bash
.venv/bin/python scripts/run_benchmark.py \
  --models smolvlm-256m qwen3-vl-2b qwen3-vl-4b --repeats 2
```

This uses the same four source images and surface-observation prompt for every model. SmolVLM and Qwen have different precision and native image processing, so this compares practical laptop configurations. It does not isolate architecture alone or measure building-inspection accuracy. See the [benchmark method](../evaluation/benchmark-method.md) and [recorded findings](../evaluation/model-findings.md).

Sources: [official Ollama release](https://github.com/ollama/ollama/releases/tag/v0.34.2), [Qwen3-VL 2B model](https://ollama.com/library/qwen3-vl:2b-instruct), [4B model](https://ollama.com/library/qwen3-vl:4b-instruct), [local server settings](https://docs.ollama.com/faq), and [chat API](https://docs.ollama.com/api/chat).
