"""Prepare small research examples and clearly labelled synthetic control images.
CrackForest images retain their original non-commercial research terms.
Copyright (c) 2026 Imarah.tech. All rights reserved, except third-party images.
"""

import hashlib
import json
import random
from pathlib import Path

import httpx
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "benchmarks/fixtures"
DEST.mkdir(parents=True, exist_ok=True)
manifest = []
for number, name in [
    (1, "Road surface · branching crack"),
    (3, "Road surface · fine crack"),
]:
    filename = f"crackforest-{number:03}.jpg"
    url = f"https://raw.githubusercontent.com/cuilimeng/CrackForest-dataset/master/image/{number:03}.jpg"
    path = DEST / filename
    if not path.exists():
        response = httpx.get(url, timeout=30, follow_redirects=True)
        response.raise_for_status()
        path.write_bytes(response.content)
    with Image.open(path) as image:
        width, height = image.size
    manifest.append(
        {
            "id": f"cfd-{number:03}",
            "name": name,
            "file": filename,
            "kind": "Research photograph · road surface",
            "description": "CrackForest research photo. Useful for a smoke test, not building-specific validation.",
            "source": url,
            "license": "Non-commercial research only; see SOURCES.md",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "width": width,
            "height": height,
            "demo_boxes": [],
        }
    )

random.seed(42)
image = Image.new("RGB", (512, 384), (187, 184, 174))
pixels = image.load()
for y in range(image.height):
    for x in range(image.width):
        noise = random.randint(-11, 11)
        pixels[x, y] = (187 + noise, 184 + noise, 174 + noise)
image.save(DEST / "synthetic-intact.jpg", quality=92)
manifest.append(
    {
        "id": "synthetic-intact",
        "name": "Unbroken surface · control",
        "file": "synthetic-intact.jpg",
        "kind": "Synthetic control",
        "description": "A generated texture with no drawn crack. Tests whether a model invents a defect.",
        "source": "scripts/prepare_fixtures.py; seed 42",
        "license": "Imarah.tech",
        "demo_boxes": [],
    }
)
cracked = image.copy()
draw = ImageDraw.Draw(cracked)
draw.line(
    [
        (261, 20),
        (253, 62),
        (268, 92),
        (250, 135),
        (270, 165),
        (247, 201),
        (262, 240),
        (245, 281),
        (253, 322),
        (242, 368),
    ],
    fill=(39, 38, 34),
    width=5,
)
draw.line([(250, 135), (221, 147), (196, 179), (178, 185)], fill=(49, 47, 43), width=3)
cracked.save(DEST / "synthetic-crack.jpg", quality=92)
manifest.append(
    {
        "id": "synthetic-crack",
        "name": "Wall crack · illustration",
        "file": "synthetic-crack.jpg",
        "kind": "Synthetic illustration",
        "description": "A drawn crack used to explain the interface. This is not a real site photograph.",
        "source": "scripts/prepare_fixtures.py; seed 42",
        "license": "Imarah.tech",
        "demo_boxes": [
            {
                "label": "Illustrative crack region",
                "confidence": None,
                "box": [170, 14, 285, 375],
            }
        ],
    }
)
building_sources = DEST / "building-samples.json"
if building_sources.exists():
    for sample in json.loads(building_sources.read_text()):
        path = DEST / sample["file"]
        if not path.exists():
            response = httpx.get(sample["source"], timeout=90, follow_redirects=True)
            response.raise_for_status()
            path.write_bytes(response.content)
        if hashlib.sha256(path.read_bytes()).hexdigest() != sample["sha256"]:
            raise SystemExit(f"Source image checksum changed: {sample['file']}")
        manifest.append(sample)

for sample in manifest:
    sample.setdefault("benchmark_group", "baseline")
    sample.setdefault("sha256", hashlib.sha256((DEST / sample["file"]).read_bytes()).hexdigest())
(DEST / "manifest.json").write_text(json.dumps(manifest, indent=2))
# App icons are simple original geometry and have no external font or image dependency.
for size in (192, 512):
    icon = Image.new("RGB", (size, size), "#183e35")
    drawing = ImageDraw.Draw(icon)
    scale = size / 64
    for line in [
        [(15, 47), (15, 26), (32, 16), (49, 26), (49, 47)],
        [(25, 47), (25, 32), (32, 28), (39, 32), (39, 47)],
        [(32, 16), (32, 28)],
        [(15, 26), (25, 32)],
        [(49, 26), (39, 32)],
    ]:
        drawing.line(
            [(int(x * scale), int(y * scale)) for x, y in line],
            fill="#f1efe3",
            width=max(3, int(3 * scale)),
            joint="curve",
        )
    icon.save(ROOT / f"frontend/public/icon-{size}.png")
print(f"Prepared {len(manifest)} samples and app icons.")
