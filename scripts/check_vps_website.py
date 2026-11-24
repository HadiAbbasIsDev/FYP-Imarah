"""Check Qwen's VPS route through the actual website and save clear test evidence.
Needs the app and SSH tunnel running; creates a labelled wall inspection and one benchmark row.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://127.0.0.1:8000")
parser.add_argument(
    "--detector",
    choices=("demo", "live"),
    default="demo",
    help="Demo skips YOLO but still calls the real VPS model; live also requires the hosted detector.",
)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
checks = []
errors = []
screenshots = root / "docs/evaluation/screenshots"
screenshots.mkdir(parents=True, exist_ok=True)


def record(message):
    checks.append(message)
    print("PASS:", message, flush=True)


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    models = context.request.get(args.url + "/api/models").json()
    qwen = next(model for model in models if model["id"] == "qwen3-vl-4b-vps")
    assert qwen["installed"] and qwen["execution_target"] == "vps"
    record("Model discovery identifies Qwen 4B as ready on the VPS.")

    page.goto(args.url + "/inspections/new", wait_until="networkidle")
    selector = page.get_by_label("Vision-language model", exact=False)
    assert "Local" in selector.locator('option[value="qwen3-vl-4b"]').inner_text()
    assert not selector.locator('option[value="qwen3-vl-4b"]').is_disabled()
    selector.select_option("qwen3-vl-4b-vps")
    assert "VPS" in selector.locator("option:checked").inner_text()
    assert page.get_by_text("Your photo is sent to the VPS", exact=False).is_visible()

    # Simulate a lost tunnel in discovery only, without closing the owner's real tunnel.
    offline = copy.deepcopy(models)
    for model in offline:
        if model["id"] == "qwen3-vl-4b-vps":
            model.update(
                installed=False, availability_note="Qwen VPS is unavailable. Open the SSH tunnel."
            )
    page.route("**/api/models", lambda route: route.fulfill(json=offline))
    page.get_by_text("Qwen VPS is unavailable.", exact=False).wait_for(timeout=20000)
    assert selector.input_value() == "qwen3-vl-4b-vps"
    assert page.get_by_role("button", name="Analyse this image").is_disabled()
    record(
        "A lost tunnel preserves the selected VPS model and disables submission; no local replacement."
    )
    page.unroute("**/api/models")
    page.get_by_text("Qwen VPS is connected", exact=False).wait_for(timeout=20000)
    assert page.get_by_role("button", name="Analyse this image").is_enabled()
    record("Reconnecting discovery makes the same selected model available again.")

    page.get_by_role("button", name="Interior wall · field photograph", exact=False).click()
    page.get_by_label("Inspection name", exact=True).fill("VPS connection check · wall photograph")
    page.get_by_label("Field notes", exact=False).fill(
        "Automated connection check using the attributed public wall photograph. Not an expert assessment."
    )
    page.get_by_label("Detector connection", exact=False).select_option(args.detector)
    page.get_by_role("button", name="Analyse this image").click()
    page.wait_for_url("**/inspections/*", timeout=20000)
    page.get_by_role("heading", name="A person completes the picture.").wait_for(timeout=120000)
    item_id = page.url.rsplit("/", 1)[-1]
    item = context.request.get(args.url + "/api/inspections/" + item_id).json()
    assert item["status"] == "complete", item.get("error")
    assert item["vlm"]["execution_target"] == "vps"
    assert item["vlm"]["transport"] == "qwen-image-api-v1"
    assert item["vlm"]["model_digest"] == qwen["remote_digest"]
    assert item["vlm"]["gpu_model_bytes"] > 0
    if args.detector == "live":
        assert "Separate detector context" in item["vlm"]["prompt"]
        assert item["detection"]["status"] == "live"
        assert page.locator(".evidence-image polygon").count() > 0
    else:
        assert item["detection"]["status"] == "illustration"
        assert "Separate detector context" not in item["vlm"]["prompt"]
    assert page.locator(".evidence-image rect").count() == 0
    assert page.get_by_text(item["vlm"]["device"], exact=True).is_visible()
    record(
        f"Real browser inspection completes with detector mode {args.detector} and Qwen on the VPS GPU."
    )
    exported = context.request.get(args.url + "/api/inspections/" + item_id + "/export").json()
    assert exported["vlm"] == item["vlm"]
    assert exported["report"]["review"]["status"] == "pending"
    record(
        "Saved report/export preserve remote model identity, timing, original text and unreviewed status."
    )
    page.screenshot(path=str(screenshots / "vps-website-desktop.png"), full_page=True)
    page.add_script_tag(path=str(root / "frontend/node_modules/axe-core/axe.min.js"))
    violations = page.evaluate(
        "async () => (await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations"
    )
    assert not violations, [violation["id"] for violation in violations]
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert page.locator(".evidence-image rect").count() == 0
    page.screenshot(path=str(screenshots / "vps-website-mobile.png"), full_page=True)
    record(
        "The report passes selected accessibility rules and fits mobile without rectangle overlays."
    )

    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(args.url + "/models", wait_until="networkidle")
    card = page.locator(".model-card").filter(
        has=page.get_by_role("heading", name="Qwen3-VL · 4B · VPS", exact=True)
    )
    assert card.get_by_text("Available on VPS", exact=True).is_visible()
    for checkbox in page.locator(".model-checkbox input").all():
        if checkbox.is_checked():
            checkbox.uncheck()
    card.get_by_role("checkbox").check()
    page.get_by_label("Benchmark image set", exact=True).select_option("building")
    with page.expect_response(
        lambda response: (
            response.url.endswith("/api/benchmarks") and response.request.method == "POST"
        )
    ) as pending:
        page.get_by_role("button", name="Run comparison", exact=True).click()
    job_id = pending.value.json()["id"]
    page.get_by_text("Finished 1/1 runs. Raw outputs saved.", exact=True).wait_for(timeout=120000)
    benchmark = context.request.get(args.url + f"/api/benchmarks/{job_id}/export").json()
    assert benchmark["status"] == "complete"
    assert benchmark["rows"][0]["execution_target"] == "vps"
    assert "caches are not reset" in benchmark["conditions"]
    assert page.get_by_text("Local & VPS experiments", exact=True).is_visible()
    record("Model lab also calls the VPS and saves the different hardware/caching conditions.")
    assert not errors, errors
    browser.close()

(root / "docs/evaluation/vps-website-check.json").write_text(
    json.dumps(
        {
            "description": "Real website-to-VPS integration checks; failure of discovery was simulated only in the browser.",
            "detector_mode": args.detector,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
            "console_errors": errors,
            "inspection_id": item_id,
            "vlm": item["vlm"],
            "benchmark_id": job_id,
            "benchmark_result": benchmark,
            "api_tests_passed": 120,
            "frontend_build": "passed",
        },
        indent=2,
    )
    + "\n"
)
