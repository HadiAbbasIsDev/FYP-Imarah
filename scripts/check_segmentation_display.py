"""Check that reports draw segmentation only, including older and incomplete records.
Use a running app with a saved live inspection: python scripts/check_segmentation_display.py
Browser-only fixtures test missing masks without changing the database or calling YOLO.
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
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
destination = root / "docs/evaluation/screenshots"
destination.mkdir(parents=True, exist_ok=True)
checks = []
errors = []


def assert_overlay(page, count):
    assert page.locator(".evidence-image polygon").count() == count
    assert page.locator(".evidence-image rect").count() == 0
    assert page.get_by_label("Overlay view").count() == 0
    assert page.locator("option").filter(has_text="Bounding boxes").count() == 0


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    # Simulate the old cached shell before the new worker activates.
    page.goto(args.url + "/manifest.webmanifest")
    page.evaluate("async () => { await caches.open('imarah-shell-v1'); }")
    records = context.request.get(args.url + "/api/inspections").json()
    live = [
        item
        for item in records
        if item["mode"] == "live"
        and item.get("detection")
        and any(region.get("polygon") for region in item["detection"]["boxes"])
    ]
    assert live, "Create a live inspection with segmentation before running this check."
    for item in live[:3]:
        page.goto(args.url + "/inspections/" + item["id"], wait_until="networkidle")
        expected = [
            region["polygon"] for region in item["detection"]["boxes"] if region.get("polygon")
        ]
        assert_overlay(page, len(expected))
        actual = page.locator(".evidence-image polygon").evaluate_all(
            "nodes => nodes.map(node => node.getAttribute('points').split(' ').map(pair => pair.split(',').map(Number)))"
        )
        assert actual == expected
    checks.append("Latest live reports draw exact saved polygons with no boxes or box selector.")
    page.evaluate("async () => { await navigator.serviceWorker.ready; }")
    page.wait_for_function("async () => !(await caches.keys()).includes('imarah-shell-v1')")
    checks.append("Updated service worker removes the old app-shell cache.")

    item = live[0]
    url = args.url + "/inspections/" + item["id"]
    api_url = args.url + "/api/inspections/" + item["id"]
    page.goto(url, wait_until="networkidle")
    count = sum(bool(region.get("polygon")) for region in item["detection"]["boxes"])
    page.get_by_role("button", name="Hide regions", exact=True).click()
    assert_overlay(page, 0)
    page.get_by_role("button", name="Show regions", exact=True).click()
    assert_overlay(page, count)
    checks.append("Hide/show toggles segmentation without introducing rectangles.")
    with page.expect_download() as pending:
        page.get_by_role("link", name="Export JSON", exact=True).click()
    pending.value.save_as(destination / "segmentation-only-export.json")
    assert json.loads((destination / "segmentation-only-export.json").read_text()) == item
    checks.append("Export preserves the original detector evidence and report.")
    page.add_script_tag(path=str(root / "frontend/node_modules/axe-core/axe.min.js"))
    violations = page.evaluate(
        "async () => (await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations"
    )
    assert not violations, [violation["id"] for violation in violations]
    checks.append("Report has no violations in the selected accessibility rules.")
    page.screenshot(path=str(destination / "segmentation-only-desktop.png"), full_page=True)
    page.emulate_media(media="print")
    assert_overlay(page, count)
    page.pdf(path=str(destination / "segmentation-only.pdf"), format="A4", print_background=True)
    page.emulate_media(media="screen")
    for width in (390, 768):
        page.set_viewport_size({"width": width, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert (
            page.locator(".evidence-image img").bounding_box()
            == page.locator(".evidence-image svg").bounding_box()
        )
        assert_overlay(page, count)
    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(path=str(destination / "segmentation-only-mobile.png"), full_page=True)
    checks.append("Print and mobile views retain aligned polygons without rectangles.")

    # Fixtures are intercepted responses only; nothing is written to saved inspections.
    for case in ("legacy", "mixed", "empty", "demo"):
        fixture = copy.deepcopy(item)
        if case in ("legacy", "demo"):
            for region in fixture["detection"]["boxes"]:
                region.pop("polygon", None)
            expected_count = 0
            if case == "demo":
                fixture["mode"] = "demo"
                fixture["detection"]["status"] = "illustration"
        elif case == "mixed":
            region = copy.deepcopy(fixture["detection"]["boxes"][0])
            region.pop("polygon", None)
            fixture["detection"]["boxes"].append(region)
            expected_count = count
        else:
            fixture["detection"]["boxes"] = []
            expected_count = 0
        page.route(api_url, lambda route: route.fulfill(json=fixture))
        page.goto(url, wait_until="networkidle")
        assert_overlay(page, expected_count)
        if case == "legacy":
            assert page.get_by_text("No segmentation outlines were saved", exact=False).is_visible()
        if case == "mixed":
            assert page.get_by_text(
                "Some regions have no saved outline and are not drawn.", exact=False
            ).is_visible()
        if expected_count == 0:
            assert page.get_by_role("button", name="Hide regions", exact=True).count() == 0
        page.unroute(api_url)
        checks.append(f"Browser-only {case} fixture never falls back to rectangles.")
    assert not errors, errors
    browser.close()

report = {
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "purpose": "Regression check: inspection overlays must display segmentation only.",
    "inspection_ids": [item["id"] for item in live[:3]],
    "checks": checks,
    "console_errors": errors,
    "accessibility_violations": len(violations),
    "fixtures_write_to_database": False,
}
(root / "docs/evaluation/segmentation-only-check.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
print(f"Passed {len(checks)} segmentation-only checks.")
