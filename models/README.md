# Local model workspace

`registry.json` keeps the original shortlist visible and adds two practical CPU baselines. Each record names a model repository, role and runtime. Hugging Face models have pinned revisions; the two Qwen3-VL instruct tags have pinned Ollama manifest digests. Downloaded folders are ignored by Git.

## Models implemented for this laptop

| Local ID | Official checkpoint | Weight file size |
| --- | --- | --- |
| `smolvlm-256m` | [HuggingFaceTB/SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) | 513,028,808 bytes |
| `smolvlm-500m` | [HuggingFaceTB/SmolVLM-500M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct) | 1,015,025,832 bytes |

These are additional baselines, not replacements for the team's full comparison plan. They are in the same model family, so their comparison does not establish which architecture is best.

```bash
.venv/bin/python scripts/download_models.py
```

The downloader pins revisions, resumes partial downloads, checks free disk space and downloads weights/configuration only. Inference does not use `trust_remote_code` and does not download anything. The `READY` file is written after the download succeeds. Keep at least 900 MB spare; this is a working-space guard, not a complete estimate for installing new dependencies.

## Original shortlist

| Candidate | Current adapter status |
| --- | --- |
| [Qwen3-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct) | Project-local Ollama adapter; see the recorded experiments for completed runs |
| [SmolVLM2-2.2B-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct) | Additional Transformers adapter planned |
| [Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct) | Project-local Ollama adapter; main candidate from the team's list |
| [InternVL2_5-4B](https://huggingface.co/OpenGVLab/InternVL2_5-4B) | Independent model family; adapter and evaluation planned |
| [Qwen2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) | Optional Ollama request path; not installed or tested |

The existing system Ollama installation is `0.11.4`; the [Qwen3-VL model page](https://ollama.com/library/qwen3-vl:2b-instruct) requires `0.12.7` or later. The continuation therefore installs verified **0.34.2** CPU runtime files in `.runtime/ollama/`, using port 11435 and `models/ollama/`. No system installation or unrelated `gemma-local` model was replaced.

The app discovers installed tags from the project server and checks each pinned digest. A missing, changed or unavailable tag stays disabled. The worker checks vision capability before sending a photograph. These checks establish readiness to attempt inference; only a completed experiment establishes that a model actually ran.

See [the local Qwen guide](../docs/guides/local-qwen.md) for installation, startup, download commands and runtime limits. The normal 2B/4B instruct models use Q4_K_M language weights and are about 1.89 GB / 3.30 GB. Setup connection failures do not create successful benchmark rows. All final model layers must match the hashes in their official manifests.

## Adding another model

1. Check current official model instructions, licence, disk size and runtime compatibility.
2. Add an explicit registry record and pinned revision where supported.
3. Add a small adapter if the processor/template differs from the tested SmolVLM path.
4. Try one image before running a comparison. Save failures too.
5. Run matched image/prompt comparisons and update the experiment documentation.

Do not download all large checkpoints at once on this disk. We did not fine-tune any VLM during Phase 1. See [the benchmark method](../docs/evaluation/benchmark-method.md) for the evaluation plan.
