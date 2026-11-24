"""Check important desktop/mobile flows in a real Chromium browser.
Use --live to create one real local-model inspection and test its review/export journey.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://127.0.0.1:8000")
parser.add_argument("--live", action="store_true")
parser.add_argument(
    "--model", default="smolvlm-256m", help="Installed model ID for the real inspection check."
)
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs/evaluation/screenshots"
DEST.mkdir(exist_ok=True, parents=True)
report = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "checks": [],
    "console_errors": [],
    "accessibility": [],
    "live": args.live,
    "model_id": args.model if args.live else None,
}


def record(name):
    report["checks"].append(name)
    print("PASS:", name, flush=True)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1440, "height": 1000},
        reduced_motion="reduce",
        accept_downloads=True,
    )
    page = context.new_page()
    page.on("pageerror", lambda error: report["console_errors"].append(str(error)))
    routes = [
        ("/", "Overview"),
        ("/inspections", "Inspections"),
        ("/inspections/new", "New inspection"),
        ("/models", "Model lab"),
        ("/site", "Site management"),
        ("/monitoring", "Monitoring"),
        ("/urban", "Urban analysis"),
        ("/roadmap", "Roadmap"),
    ]
    axe = ROOT / "frontend/node_modules/axe-core/axe.min.js"
    for route, name in routes:
        page.goto(args.url + route, wait_until="networkidle")
        page.locator("h1").wait_for()
        assert page.locator("h1").count() == 1
        assert not page.get_by_role("alert").count(), f"API error on {route}"
        record(f"Desktop route: {name}")
        if axe.exists():
            page.add_script_tag(path=str(axe))
            findings = page.evaluate(
                "async () => (await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations"
            )
            report["accessibility"].append(
                {
                    "route": route,
                    "violations": [
                        {
                            "id": v["id"],
                            "impact": v["impact"],
                            "nodes": [
                                {
                                    "target": n["target"],
                                    "summary": n.get("failureSummary", ""),
                                }
                                for n in v["nodes"]
                            ],
                        }
                        for v in findings
                    ],
                }
            )
        if route in ["/", "/models", "/site", "/roadmap"]:
            page.screenshot(
                path=str(DEST / (name.lower().replace(" ", "-") + "-desktop.png")),
                full_page=True,
            )
    (ROOT / "docs/evaluation/browser-results.json").write_text(json.dumps(report, indent=2))
    page.goto(args.url + "/models", wait_until="networkidle")
    page.get_by_label("Benchmark image set", exact=True).select_option("building")
    assert page.get_by_text("1 image per model", exact=False).is_visible()
    page.get_by_label("Benchmark image set", exact=True).select_option("baseline")
    assert page.get_by_text("4 images per model", exact=False).is_visible()
    record("Benchmark image sets keep the original comparison and new wall photo separate")
    if page.locator(".model-checkbox input").count() >= 4:
        page.locator(".model-checkbox input:not(:checked)").first.check()
        assert page.locator(".model-checkbox input:checked").count() == 3
        assert page.locator(".model-checkbox input:not(:checked):enabled").count() == 0
        page.locator(".model-checkbox input:checked").first.uncheck()
        assert page.locator(".model-checkbox input:not(:checked):enabled").count() >= 2
        record("Four installed models respect the three-model comparison limit")
    page.goto(args.url + "/inspections/new", wait_until="networkidle")
    page.get_by_role("button", name="Interior wall · field photograph", exact=False).click()
    assert page.get_by_role("link", name="Cracked wall 03.jpg", exact=True).is_visible()
    assert page.get_by_role("link", name="CC BY-SA 4.0", exact=True).is_visible()
    record("Public wall sample shows its photographer, source and licence")
    page.goto(args.url + "/site", wait_until="networkidle")
    page.get_by_role("button", name="View Usman Ahmed", exact=True).click()
    assert page.get_by_text("Usman Ahmed · sample assessment").is_visible()
    page.get_by_label("Filter workers").select_option("PPE follow-up")
    assert page.locator("tbody tr").count() == 2
    page.get_by_role("button", name="Materials", exact=True).click()
    assert page.get_by_role("heading", name="Cement", exact=True).is_visible()
    page.get_by_role("button", name="Records", exact=True).click()
    assert page.get_by_role("heading", name="Payroll records", exact=True).is_visible()
    record("Workforce filter, assessment, materials and records")
    page.goto(args.url + "/monitoring", wait_until="networkidle")
    page.get_by_role("button", name="Relative humidity", exact=False).click()
    assert page.get_by_role("heading", name="Relative humidity through the day").is_visible()
    record("Sensor selection changes the displayed trend")
    page.goto(args.url + "/urban", wait_until="networkidle")
    page.get_by_label("Explore an example area").select_option("1")
    assert page.get_by_role("heading", name="Saddar", exact=True).is_visible()
    record("Schematic area selection changes the example indicators")

    if args.live:
        page.goto(args.url + "/inspections/new", wait_until="networkidle")
        page.get_by_label("Vision-language model", exact=False).select_option(args.model)
        page.get_by_label("Inspection name", exact=True).fill("Evaluation sample · synthetic wall")
        page.get_by_label("Location", exact=False).fill(
            "Demonstration fixture · not a real building"
        )
        page.get_by_label("Field notes", exact=False).fill(
            "Created by the automated browser workflow test; the image is synthetic."
        )
        page.get_by_role("button", name="Analyse this image").click()
        page.wait_for_url("**/inspections/*", timeout=20000)
        page.get_by_role("heading", name="A person completes the picture.").wait_for(timeout=360000)
        assert page.get_by_text("Unreviewed output", exact=True).is_visible()
        record("Real image -> local VLM -> persisted inspection draft")
        page.get_by_label("Reviewer name", exact=True).fill("Workflow test (automated)")
        page.get_by_label("Review notes", exact=True).fill(
            "This checks that review notes can be saved. It is not an expert assessment or a human validation of the model."
        )
        page.get_by_role("button", name="Save review", exact=True).click()
        page.get_by_text("Review recorded", exact=True).wait_for()
        with page.expect_download() as download_info:
            page.get_by_role("link", name="Export JSON", exact=True).click()
        downloaded = download_info.value
        destination = DEST / "inspection-export.json"
        downloaded.save_as(destination)
        item = json.loads(destination.read_text())
        assert item["vlm"]["text"] and item["report"]["review"]["status"] == "reviewed"
        assert item["vlm"]["model_id"] == args.model
        assert item["detection"]["status"] == "illustration"
        report["inspection_id"] = item["id"]
        page.screenshot(path=str(DEST / "inspection-report-desktop.png"), full_page=True)
        page.pdf(path=str(DEST / "inspection-report.pdf"), format="A4", print_background=True)
        record("Review save, JSON download and printable PDF with real model output")

    for width in [390, 768]:
        page.set_viewport_size({"width": width, "height": 844})
        for route, name in routes:
            page.goto(args.url + route, wait_until="networkidle")
            page.locator("h1").wait_for()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
                f"Page overflow: {name} at {width}"
            )
            if width == 390 and route in ["/", "/inspections/new", "/models"]:
                page.screenshot(
                    path=str(DEST / (name.lower().replace(" ", "-") + "-mobile.png")),
                    full_page=True,
                )
        record(f"All eight routes fit a {width}px viewport")
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(args.url, wait_until="networkidle")
    page.get_by_role("button", name="Open navigation", exact=True).click()
    page.get_by_role("navigation", name="Main navigation").get_by_role("link").filter(
        has_text="Building monitoring"
    ).click()
    page.get_by_role("heading", name="Listen to the building over time.").wait_for()
    page.wait_for_function("document.querySelector('.sidebar').getBoundingClientRect().right <= 1")
    record("Mobile navigation drawer opens, navigates and closes")
    manifest = page.evaluate("async()=>await (await fetch('/manifest.webmanifest')).json()")
    assert manifest["display"] == "standalone" and len(manifest["icons"]) == 2
    page.goto(args.url, wait_until="networkidle")
    page.evaluate("async () => { await navigator.serviceWorker.ready; }")
    page.reload(wait_until="networkidle")
    context.set_offline(True)
    page.reload(wait_until="domcontentloaded")
    page.get_by_role("heading", name="See the details. Build with confidence.").wait_for()
    assert page.get_by_text("You’re offline.", exact=False).is_visible()
    record("PWA manifest and offline shell; offline API errors remain visible")
    context.set_offline(False)
    browser.close()

report["accessibility_violation_count"] = sum(len(p["violations"]) for p in report["accessibility"])
(ROOT / "docs/evaluation/browser-results.json").write_text(json.dumps(report, indent=2))
assert not report["console_errors"], report["console_errors"]
assert not report["accessibility_violation_count"], (
    "Accessibility violations are recorded in docs/evaluation/browser-results.json"
)
print(
    f"Finished {len(report['checks'])} checks. Accessibility rule violations: {report['accessibility_violation_count']}"
)
