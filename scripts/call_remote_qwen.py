"""Send a photograph to Qwen through the PC's SSH tunnel and print its actual answer.
Use: python scripts/call_remote_qwen.py --image path/to/photo.jpg
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import argparse
import json
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--url", default="http://127.0.0.1:18084")
    parser.add_argument(
        "--prompt", help="Optional task description; otherwise use the surface-observation prompt."
    )
    parser.add_argument("--max-tokens", type=int, default=140)
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error("The image file does not exist.")
    if args.image.stat().st_size > 10 * 1024 * 1024:
        parser.error("Choose an image no larger than 10 MB.")
    data = {"max_tokens": str(args.max_tokens)}
    if args.prompt:
        data["prompt"] = args.prompt
    try:
        with args.image.open("rb") as image, httpx.Client(timeout=330, trust_env=False) as client:
            response = client.post(
                args.url.rstrip("/") + "/v1/analyze",
                data=data,
                files={"file": (args.image.name, image, "application/octet-stream")},
            )
            response.raise_for_status()
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except httpx.HTTPStatusError as exc:
        raise SystemExit(
            f"Qwen API returned HTTP {exc.response.status_code}: {exc.response.text[:500]}"
        ) from exc
    except httpx.HTTPError as exc:
        raise SystemExit(
            "Cannot reach Qwen. Check the SSH tunnel and server service status."
        ) from exc


if __name__ == "__main__":
    main()
