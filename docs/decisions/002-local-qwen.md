# Decision 002: add the Qwen shortlist without changing the small baselines

**Date:** 19 September 2026. **Scope:** the September laptop demonstration.

The first build used two small SmolVLM models because the disk was nearly full. After the team freed space, around 23 GB was available. We could then test the proposed Qwen3-VL 2B and 4B models without removing unrelated work.

We chose quantized local inference through Ollama. The laptop has no NVIDIA/CUDA device, so the tested configuration requests CPU execution and four threads. The old system Ollama was too old for Qwen3-VL. Installing a pinned copy inside `.runtime/ollama/` lets us reproduce the project setup while leaving the system copy and its existing model store alone.

The app owns the inspection/report workflow; Ollama owns model execution. A short Python worker connects over loopback, sends one thumbnail and the fixed prompt, saves the raw output and measured timings, then exits. Streaming gives a timed-out worker a connection that can close. Requests unload models afterward, and the next run checks that its previous copy has unloaded.

There are two important comparison limits. First, Q4_K_M Qwen and float32 SmolVLM do not share numeric precision or native image processing. We compare useful laptop configurations, not architecture in isolation. Second, an HTTP client's memory tells us almost nothing about the model process; that measurement stays blank for Ollama.

We also added one public interior-wall photo, with its original CC BY-SA 4.0 attribution. It makes the building-inspection idea easier to demonstrate. It stays separate from the original four-image set and does not become a claimed holdout dataset simply because it is a new file in our repository.

The result is still a small student project: a registry, one adapter per runtime, a local launcher, and explicit failure messages. We have not added fine-tuning, a GPU service or a multi-user model cluster. Installation details are in [the Qwen guide](../guides/local-qwen.md); actual outcomes are in [model findings](../evaluation/model-findings.md).
