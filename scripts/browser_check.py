"""Exercise the real static site locally or over HTTPS; retain a test receipt."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
from urllib.parse import urljoin

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@contextmanager
def site_url(remote):
    if remote:
        yield remote.rstrip("/") + "/"
        return
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "_site")))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def check(url, channel, output, expected_sha):
    checks, errors, urls = [], [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel=channel)
        try:
            context = browser.new_context(viewport={"width": 1200, "height": 900}, locale="en-GB", accept_downloads=True)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))

            def visit(path):
                address = urljoin(url, path)
                response = page.goto(address, wait_until="networkidle")
                assert response and response.status == 200, address
                urls.append(page.url)

            release_response = context.request.get(urljoin(url, "release.json"), headers={"Cache-Control": "no-cache"})
            assert release_response.ok
            release = release_response.json()
            if expected_sha:
                assert release["commit"] == expected_sha, "Published commit differs from the authorised revision"
            for item in release["files"]:
                response = context.request.get(urljoin(url, item["path"]), headers={"Cache-Control": "no-cache"})
                assert response.ok, item["path"]
                assert sha256(response.body()).hexdigest() == item["sha256"], item["path"]
            checks.append("Every published file responds and matches the release hash")

            visit("")
            assert page.get_by_role("heading", name="Useful information for the next action").is_visible()
            page.screenshot(path=output / "landing-desktop.png")
            for width in [390, 724]:
                page.set_viewport_size({"width": width, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Landing overflow at {width}"
            page.screenshot(path=output / "landing-mobile.png")
            checks.append("Landing navigation and 390/724 pixel layouts")

            with page.expect_download() as event:
                page.get_by_role("link", name="Download the Word guide", exact=True).click()
            downloaded = event.value
            assert downloaded.suggested_filename == "FTK_OKF_illustrated_walkthrough.docx"
            assert sha256(Path(downloaded.path()).read_bytes()).hexdigest() == next(i["sha256"] for i in release["files"] if i["path"].endswith(".docx"))
            checks.append("Word guide downloaded through the actual page link")

            page.get_by_role("link", name="Read the walkthrough", exact=True).click()
            assert page.url.endswith("FTK_OKF_illustrated_walkthrough.html")
            urls.append(page.url)
            assert page.locator(".step").count() == 22
            assert page.locator("figure").count() == 32
            page.get_by_role("button", name="Manager account", exact=True).click()
            assert page.locator(".novice:visible").count() == 0
            assert page.locator(".manager:visible").count() == 22
            page.get_by_role("button", name="Novice account", exact=True).click()
            assert page.locator(".manager:visible").count() == 0
            page.get_by_role("button", name="Both accounts", exact=True).click()
            for img in page.locator("figure img").all():
                img.scroll_into_view_if_needed()
                img.evaluate("image => image.decode()")
            assert page.locator("figure img").evaluate_all("images => images.every(image => image.naturalWidth > 0)")
            page.get_by_role("button", name="Enlarge figure 3", exact=True).click()
            assert page.locator("dialog:visible").count() == 1
            page.keyboard.press("Escape")
            assert page.locator("dialog:visible").count() == 0
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.locator("#step-03").scroll_into_view_if_needed()
            page.screenshot(path=output / "guide-mobile.png")
            checks.append("22 guide steps, 32 decoded images, both accounts, image enlargement and responsive layout")

            visit("FTK_OKF_handover.html")
            page.set_viewport_size({"width": 1200, "height": 900})
            assert "13 concepts" in page.locator("#counts").text_content()
            page.locator("#tab-relationships").click()
            assert page.locator("#relationship-rows tr").count() == 17
            page.locator("#relation-search").fill("owned")
            assert page.locator("#relationship-rows tr").count() == 3
            page.locator("#relation-search").fill("")
            page.locator("#tab-handover").click()
            assert "CHECK PASSED" in page.locator("#check-result").text_content()
            page.locator("#break-copy").click()
            assert "CHECK FAILED" in page.locator("#check-result").text_content()
            page.locator("#restore-copy").click()
            assert "CHECK PASSED" in page.locator("#check-result").text_content()
            checks.append("17 relationships, search, corrupted-copy rejection and restoration")
            page.locator("#tab-reuse").click()
            assert page.locator("#comparison-description").is_visible()
            page.locator("#tab-ai").click()
            assert "Use only the attached fictional" in page.locator("#ai-prompt").input_value()
            page.locator("#questions button").first.click()
            assert "Authored reference answer" in page.locator("#reference-answer").text_content()
            with page.expect_download() as event:
                page.locator("#download-bundle").click()
            bundle = json.loads(Path(event.value.path()).read_text())
            assert bundle["okf_version"] == "0.2"
            assert bundle["meta"]["release_grade"] is False
            checks.append("Reuse and AI panels, authored reference answer, real JSON download")
            page.locator("#copy-prompt").click()
            expect(page.locator("#toast")).to_contain_text(re.compile(r"Copied|Clipboard unavailable"))
            checks.append("Copy prompt reports success or its documented download fallback")
            page.screenshot(path=output / "demo-ai.png")
            visit("limits.html")
            assert page.get_by_role("heading", name="Evidence and limitations", exact=True).is_visible()
            checks.append("Limitations page navigated successfully")
            assert not errors, errors
            return {"passed": True, "base_url": url, "commit": release["commit"], "browser": browser.version,
                    "actual_navigation": True, "injected_html": False, "urls": urls, "checks": checks, "page_errors": errors}
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Check a deployed URL instead of starting a loopback server")
    parser.add_argument("--channel", help="Optional installed browser channel, for example chrome")
    parser.add_argument("--expected-sha", help="Require this independently supplied published commit")
    args = parser.parse_args()
    output = ROOT / "output" / ("live" if args.url else "local")
    output.mkdir(parents=True, exist_ok=True)
    try:
        with site_url(args.url) as url:
            receipt = check(url, args.channel, output, args.expected_sha)
    except Exception as error:
        (output / "browser-receipt.json").write_text(json.dumps({"passed": False, "error": str(error)}, indent=2) + "\n")
        raise
    (output / "browser-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
