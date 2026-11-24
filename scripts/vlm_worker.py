"""Read a photo with a local VLM and return its words and measured runtime.
This process exits after each run, releasing model memory and allowing timeouts.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json
import os
import platform
import sys
import time
from pathlib import Path

try:
    import resource
except ImportError:  # Windows does not provide the Unix resource module.
    resource = None

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def main():
    request = json.loads(Path(sys.argv[1]).read_text())
    output = Path(sys.argv[2])
    model_info = request["model"]
    started = time.perf_counter()
    if model_info["runtime"] == "ollama":
        from ollama_worker import run

        result = run(request)
    else:
        import torch
        import transformers
        from PIL import Image
        from transformers import AutoModelForVision2Seq, AutoProcessor

        torch.set_num_threads(4)
        torch.manual_seed(42)
        model_path = Path(__file__).resolve().parents[1] / "models" / model_info["id"]
        processor = AutoProcessor.from_pretrained(model_path, local_files_only=True)
        # The default processor enlarges small photos to 2048px and creates many tiles.
        # One 512px view makes this CPU demo practical; benchmark this trade-off separately.
        processor.image_processor.size = {"longest_edge": 512}
        processor.image_processor.do_image_splitting = False
        model = AutoModelForVision2Seq.from_pretrained(
            model_path,
            torch_dtype=torch.float32,
            _attn_implementation="eager",
            local_files_only=True,
        ).eval()
        load_ms = round((time.perf_counter() - started) * 1000)
        with Image.open(request["image_path"]) as source:
            image = source.convert("RGB")
        image.thumbnail((512, 512))
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": request["prompt"]},
                ],
            }
        ]
        prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(text=prompt, images=[image], return_tensors="pt")
        generation_start = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                max_new_tokens=request["max_new_tokens"],
                do_sample=False,
                use_cache=True,
            )
        new_tokens = generated[0, inputs["input_ids"].shape[-1] :]
        peak_mb = None
        if resource:
            divisor = 1024**2 if sys.platform == "darwin" else 1024
            peak_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / divisor, 1)
        result = {
            "text": processor.decode(new_tokens, skip_special_tokens=True).strip(),
            "load_ms": load_ms,
            "generation_ms": round((time.perf_counter() - generation_start) * 1000),
            "output_tokens": len(new_tokens),
            "peak_rss_mb": peak_mb,
            "device": "CPU · 4 threads · float32",
            "runtime": "transformers",
            "runtime_version": f"transformers {transformers.__version__}; torch {torch.__version__}",
            "image_preprocessing": {
                "version": "single-view-512-v1",
                "longest_edge": 512,
                "image_splitting": False,
                "pixel_values_shape": list(inputs["pixel_values"].shape),
            },
        }
    if not result["text"]:
        raise RuntimeError("The model returned no text.")
    result.update(
        total_ms=round((time.perf_counter() - started) * 1000),
        max_new_tokens=request["max_new_tokens"],
        seed=42,
        python_version=platform.python_version(),
    )
    output.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
