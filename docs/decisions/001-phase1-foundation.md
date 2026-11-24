# Decision 001: a small PWA foundation

**Date:** 19 September 2026. **Status:** adopted for the September prototype.

## Why a PWA

The proposal explicitly calls for a Progressive Web Application. One responsive interface lets us demonstrate the same work on a laptop and a phone. React with TypeScript provides ordinary components and useful type checking without a separate native app project. We can consider a mobile wrapper later if a device requirement justifies it.

## Why FastAPI and SQLite

The trained detector and local model tools are Python-based. Keeping the API in Python makes model integration easier for the team to understand. SQLite is enough for one local evaluation workspace and needs no service installation. The frontend can be built once and served from the same API process.

We kept the separation clear: HTTP routes, persistence, image validation, detector adaptation and VLM inference have distinct files. This is a foundation for later work, not a claim that SQLite plus an in-memory queue is already a production architecture.

## Why two smaller VLMs

The machine has an Intel i7-1355U, about 31 GiB usable RAM, integrated Intel graphics, and no NVIDIA/CUDA device. Only about 3.1 GiB disk space was free at the start. Downloading the original shortlist would have exceeded that space.

We chose the official [SmolVLM 256M](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) and [500M](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct) checkpoints as additional CPU baselines. Their checked weight files total about 1.53 GB. This gives us real observations to compare without deleting anyone's other files.

These two models belong to the same family. They provide a size comparison, not independent architectural validation. The original Qwen, InternVL and SmolVLM2 candidates remain in the registry and roadmap.

The final CPU runner uses one 512×512 view. Testing showed that the default processor enlarged the photo to 2,048 pixels and split it into tiles, making each call much slower. We keep the earlier results and record the new preprocessing version. A higher-detail tiled profile should be reconsidered during the building-specific quality study; latency alone cannot justify discarding important image detail.

## Why preserve raw text

A small VLM can make confident mistakes or ignore a requested format. If we force all output into an attractive report and hide the original, the jury cannot assess the research. We therefore display raw observations, put fixed application guidance in its own section, and keep human review separate.

## Why no synthetic accuracy score

Four example images do not constitute a held-out evaluation set. We can measure runtime and memory and examine failures. We cannot defend a building-inspection accuracy percentage from this set. The next phase needs labelled building images and a clear expert-review method before claiming quality metrics.

## Revisit this decision when

- A real endpoint and dataset clarify the detector's exact task and output.
- Multiple users need to work concurrently.
- Worker records introduce access permissions and correction/audit requirements.
- A deployment environment or available GPU changes the model budget.
- The report schema stabilizes enough to justify relational tables and migrations.
