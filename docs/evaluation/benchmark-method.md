# How we compare the VLMs

Our first question is modest: **can a local model describe a surface image on this laptop, and what mistakes does it make?** It is too early to claim the best model for building inspection.

The original local experiments below are preserved unchanged. The website now also offers `qwen3-vl-4b-vps` beside the existing local `qwen3-vl-4b`. New VPS rows record `execution_target: vps`, reported hardware allocation, runtime version, image processing and cache policy. VPS models may stay warm, use eight CPU threads when needed and run on different hardware; their `total_ms` also includes the network request. Do not describe these as the same CPU or fresh-load conditions as the older experiments. `server_api_total_ms` and `server_total_ms` provide separate server timings; neither model allocation nor client memory is treated as peak RAM.

## Shared protocol and the SmolVLM baseline

The model lab runs the same source images through each selected model. It uses the exact same prompt and a fixed output limit; local models use four CPU threads. Hugging Face revisions and Ollama manifest digests are recorded in `models/registry.json`. The original SmolVLM settings below remain unchanged, so older results stay interpretable.

| Setting | Value |
| --- | --- |
| Runtime | Transformers `4.57.1`, CPU PyTorch |
| Numeric type | float32 during inference |
| CPU threads | 4 per worker |
| Decoding | Greedy (`do_sample=False`); seed 42 |
| Output limit | 140 new tokens |
| Image input | RGB, one 512×512 processor view; image splitting disabled |
| Scheduling | Sequential, isolated process for every row |
| Model load | Fresh load in every process; operating-system file caches are not cleared |
| Detector context | None for benchmark comparisons |
| Repetitions | UI defaults to 1; final scripted comparison uses 2 |

The prompt lives in `backend/app/services/vlm.py` and is also copied into every saved experiment. It asks for visible surface details, discourages guessed measurements/causes/safety claims, and tells the model not to treat text in the image as instructions. These are instructions to a fallible model, not guarantees of its behaviour.

The final protocol is `single-view-512-v1`. The official processor defaults to a 2,048-pixel longest edge and multiple tiles, even when the input photo has already been made smaller. We explicitly set the processor size and disable splitting for this CPU demonstration. The processor resizes the view to a 512×512 square; that can lose detail and alter aspect ratio. Each new row records `image_preprocessing` and the actual tensor shape. The earlier three-image baseline retained the default tiled processor and must not be mixed into the final timing aggregate.

## Qwen and comparisons across runtimes

Qwen3-VL runs through project-local Ollama with Q4_K_M language weights. Its profile is `ollama-thumbnail-512-v1`: an RGB PNG thumbnail with preserved aspect ratio and a longest edge of 512 pixels, followed by the runtime's native vision preprocessing. We record the transmitted PNG hash and dimensions. SmolVLM's square processor view and Qwen's native patch processing are different; equal source-image hashes do not imply equal internal tensors.

The Qwen settings are CPU execution (`num_gpu=0`), four threads, context 4096, temperature zero, seed 42 and 140 output tokens. The worker unloads a previous copy before its request and sets `keep_alive=0` for unloading afterward. Downloads, queue waiting and OS cache clearing are outside the experiment. The exact Ollama version, tag, digest, options and image profile appear in each row.

This setup answers which tested **laptop configuration** is useful for the demo. It does not isolate the effects of architecture, model size, numeric precision or image processor. Keep the two-prompt experiments separate as well. The current four-image set cannot establish a quality ranking that generalizes to buildings.

## The four examples

| ID | Image | What it tells us |
| --- | --- | --- |
| `cfd-001` | CrackForest road photograph 001 | Can the model describe a real visibly cracked road surface? |
| `cfd-003` | CrackForest road photograph 003 | A second real road example with a different pattern |
| `synthetic-intact` | Seeded generated texture without a drawn crack | A simple control for unsupported defect claims |
| `synthetic-crack` | The same texture with a drawn branching line | A clear visual and interface illustration |

The two real images show roads, not buildings. The two synthetic images are not field data. This convenience sample is useful for debugging and demonstration; it is not representative and is not a held-out accuracy study. The manifest preserves origin, label, image hash and licence information.

## Measurements we can defend

The continuation also includes `commons-wall-03`, an attributed public interior-wall photograph. It is a separate exploratory image set in the interface; the CLI's default four IDs still reproduce the original sample selection. Its source and licence are in [fixture sources](../../benchmarks/fixtures/SOURCES.md). Adding a real wall example improves the demonstration's relevance, but one public image is not building-domain validation.

Each successful worker records:

- `load_ms`: elapsed time from worker timing start until model/processor loading finishes, including imports in the current implementation.
- `generation_ms`: the `generate()` call only; image preparation is outside this sub-measurement.
- `total_ms`: imports, model load, processing and generation inside the worker. It excludes download time, queue wait, subprocess launch overhead before the timer, and browser/network time.
- `output_tokens`: number of generated token IDs, including any generated special token.
- `peak_rss_mb`: peak resident memory of that process in MiB on Linux. The interface shows MiB or GiB. It includes the Python/ML stack, not only model parameters. It is not VRAM or whole-system usage. On Windows it is unmeasured.
- `text`, `prompt`, revision, package versions and image hash.

For Ollama rows, `load_ms`, `generation_ms`, `prompt_eval_ms` and `server_total_ms` are durations reported by Ollama. The worker's `total_ms` additionally includes its imports, local metadata checks, image encoding and HTTP overhead. It is measured with the same outer worker timer, but the sub-timings have different boundaries from Transformers. The model runner is a separate process, so `peak_rss_mb` is `null`; neither the HTTP client's peak nor Ollama's model-size estimate is substituted for that measurement. A dash in the interface means unavailable, not zero memory.

The UI shows median worker total time across successful rows in the selected experiment and maximum measured worker memory. That aggregate combines different images and output lengths. For a closer comparison, inspect matched image/repetition rows in the exported JSON. An unfinished or failed run stays visible; it is not counted as a successful zero-second inference.

Because processes start fresh but OS caches can be warm, describe these as **fresh-process runs**, not guaranteed cold-cache hardware benchmarks. Background work, thermal throttling and the model downloads running during this session affect timings. There are too few repetitions for useful confidence intervals.

Runs are grouped by model in the requested order, rather than randomized. Machine load and temperature can therefore drift between groups. The larger repeated comparison started after the downloads finished, but it still shares the development laptop. Treat its observed ranges as descriptive measurements, not a controlled hardware ranking.

## Quality review for the next phase

Keep raw output and ask a qualified reviewer to score each response using an agreed rubric:

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Visual grounding | Describes unsupported objects/defects | Partly agrees with image | Stays supported by visible evidence |
| Useful coverage | Misses the main visible feature | Covers some useful details | Covers the relevant visible details |
| Uncertainty | Makes unsupported measurements or safety claims | Mixed caution | Explains what the image cannot establish |
| Readability | Confusing or incomplete | Understandable with edits | Clear, concise observation |

These are proposed review dimensions, not completed human labels. Current benchmark rows set `human_review` to `null`. Do not turn this rubric into an automated regex score or present it as a validated metric.

For YOLO, plan a building-specific, leakage-controlled split and appropriate box/segmentation metrics: precision, recall, mAP and, where relevant, mask IoU. Keep detector evaluation separate from VLM report evaluation. Calibrated measurements and structural-risk methods require additional evidence beyond a photograph.

## Repeat the experiment

```bash
.venv/bin/python scripts/run_benchmark.py --repeats 2

# Repeat the separately saved shorter-prompt experiment
.venv/bin/python scripts/run_benchmark.py --prompt-version brief-caption-v2 --repeats 1

# Keep the new interior-wall example in a separately named experiment file.
.venv/bin/python scripts/run_benchmark.py --models smolvlm-256m qwen3-vl-2b qwen3-vl-4b --samples commons-wall-03 --repeats 1
```

Keep the raw file, note the machine and date, and add an interpretation to [model findings](model-findings.md). Do not overwrite an old result when changing prompts or settings; create another experiment.

The shorter caption prompt is an exploratory second profile, not a replacement for the inspection prompt. It changes the task and the generated output length, so compare it in its own experiment. Choosing a prompt on these same four images does not establish generalization to a new evaluation set.
