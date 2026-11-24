"""Export a small presentation-friendly plot from a completed real benchmark.
Use: python scripts/plot_benchmark.py benchmarks/results/bench-<id>.json
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import json
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1])
experiment = json.loads(source.read_text())
if experiment["status"] != "complete":
    raise SystemExit("Choose a completed experiment; unfinished results should not look final.")
rows = experiment["rows"]
models = sorted({row["model_id"] for row in rows})
names = [next(row["model_name"] for row in rows if row["model_id"] == model) for model in models]
labels = []
for model, name in zip(models, names):
    row = next(row for row in rows if row["model_id"] == model)
    precision = row.get("quantization") or (
        "float32" if "float32" in row.get("device", "") else "precision in raw record"
    )
    labels.append(name.replace(" · ", "\n") + "\n" + precision)
has_ollama = any(row.get("runtime") == "ollama" for row in rows)
times = [
    statistics.median(row["total_ms"] / 1000 for row in rows if row["model_id"] == model)
    for model in models
]
memory = [
    max(
        (
            row["peak_rss_mb"] / 1024
            for row in rows
            if row["model_id"] == model and row.get("peak_rss_mb") is not None
        ),
        default=None,
    )
    for model in models
]
destination = ROOT / "docs/evaluation/figures"
destination.mkdir(exist_ok=True)
fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5))
fig.patch.set_facecolor("#f7f8f3")
for axis, values, title, unit in zip(
    axes, [times, memory], ["Median elapsed time", "Peak worker memory"], ["seconds", "GiB"]
):
    axis.set_facecolor("#f7f8f3")
    measured = [value if value is not None else 0 for value in values]
    upper = max(measured) or 1
    bars = axis.bar(
        labels,
        measured,
        color=["#315e49", "#aaa07a", "#bf7859"],
        width=0.48,
    )
    axis.set_title(title, fontsize=12, loc="left", pad=19, color="#294838")
    axis.set_ylabel(unit, fontsize=10, color="#60735a")
    axis.set_ylim(0, upper * 1.3)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#dce4d3")
    axis.tick_params(axis="both", length=0, labelsize=9, colors="#536649")
    axis.yaxis.grid(True, color="#e3e9da", linewidth=0.7)
    axis.set_axisbelow(True)
    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + upper * 0.035,
            f"{value:.2f}" if value is not None else "Not reported",
            ha="center",
            fontsize=10,
            color="#294838",
        )
fig.suptitle(
    "Imarah.tech · local VLM comparison",
    x=0.07,
    y=0.98,
    ha="left",
    fontsize=16,
    color="#294838",
    fontweight="bold",
)
fig.text(
    0.07,
    0.065,
    f"{len(rows)} runs · {len({r['sample_id'] for r in rows})} example images · {experiment['repeats']} repetitions · CPU / 4 threads; precision and preprocessing differ by runtime",
    fontsize=9,
    color="#67795d",
)
fig.text(
    0.07,
    0.02,
    f"{experiment['id']} · Fresh model loads. "
    + ("Ollama peak RAM unavailable. " if has_ollama else "")
    + "Exploratory runtime measurements; not accuracy scores.",
    fontsize=8,
    color="#67795d",
)
fig.tight_layout(rect=[0.02, 0.12, 1, 0.88], w_pad=3)
for suffix in ["png", "svg"]:
    output = destination / f"{experiment['id']}.{suffix}"
    fig.savefig(
        output,
        dpi=180,
        facecolor=fig.get_facecolor(),
        metadata={"Creator": "Imarah.tech. All rights reserved."} if suffix == "svg" else None,
    )
    print(output)
