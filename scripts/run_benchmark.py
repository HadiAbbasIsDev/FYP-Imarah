"""Start a repeatable comparison through the running API and wait for its outcome.
Use: python scripts/run_benchmark.py --repeats 2
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import argparse
import time

import httpx

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://127.0.0.1:8000")
parser.add_argument("--models", nargs="+", default=["smolvlm-256m", "smolvlm-500m"])
parser.add_argument(
    "--samples",
    nargs="+",
    default=["cfd-001", "cfd-003", "synthetic-intact", "synthetic-crack"],
)
parser.add_argument("--repeats", type=int, default=1)
parser.add_argument(
    "--prompt-version",
    choices=["surface-observation-v1", "brief-caption-v2"],
    default="surface-observation-v1",
)
args = parser.parse_args()
with httpx.Client(base_url=args.url, timeout=30) as client:
    response = client.post(
        "/api/benchmarks",
        json={
            "model_ids": args.models,
            "sample_ids": args.samples,
            "repeats": args.repeats,
            "prompt_version": args.prompt_version,
        },
    )
    response.raise_for_status()
    job_id = response.json()["id"]
    print("Experiment:", job_id, flush=True)
    previous = ""
    connection_failures = 0
    while True:
        try:
            response = client.get(f"/api/jobs/{job_id}")
        except httpx.TransportError:
            connection_failures += 1
            if connection_failures > 10:
                raise SystemExit(
                    f"Cannot reconnect to the app. Experiment {job_id} may still be saved; check Model lab."
                )
            if connection_failures == 1:
                print("The app is temporarily unavailable; reconnecting to the same job.", flush=True)
            time.sleep(3)
            continue
        connection_failures = 0
        response.raise_for_status()
        job = response.json()
        if job["message"] != previous:
            print(job["message"], flush=True)
            previous = job["message"]
        if job["status"] not in ("queued", "running"):
            print(
                f"Status: {job['status']}. Results: benchmarks/results/{job_id}.json",
                flush=True,
            )
            raise SystemExit(0 if job["status"] == "complete" else 1)
        time.sleep(3)
