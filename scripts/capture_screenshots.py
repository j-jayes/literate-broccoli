"""
Capture screenshots of the Lunch Order web app user journey using Playwright.

Usage:
    python scripts/capture_screenshots.py [--url URL] [--password PASSWORD]

Screenshots are saved to slides/assets/screenshots/app/
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

APP_URL = "http://127.0.0.1:8766"
APP_PASSWORD = "Nexer Insight"
OUT_DIR = Path(__file__).resolve().parents[1] / "slides" / "assets" / "screenshots" / "app"

VIEWPORT = {"width": 1440, "height": 900}


def shot(page, name: str) -> None:
    path = OUT_DIR / name
    page.screenshot(path=str(path), full_page=False)
    print(f"  saved: {path.name}")


def run(url: str, password: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Target: {url}")
    print(f"Output: {OUT_DIR}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()

        # ── 1. Login page ────────────────────────────────────────────────────
        print("Step 1: Login page")
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector("input[type='password']", timeout=15000)
        shot(page, "01-login.png")

        # ── 2. Sign in ───────────────────────────────────────────────────────
        print("Step 2: Sign in")
        page.fill("input[type='password']", password)
        shot(page, "02-login-filled.png")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1200)

        # ── 3. Admin panel — restaurant selection ────────────────────────────
        print("Step 3: Admin panel with cached restaurants")
        shot(page, "03-admin-panel.png")

        # ── 4. Open the scraper form ─────────────────────────────────────────
        print("Step 4: 'Add another restaurant' form open")
        page.get_by_role("button", name="Add").click()
        page.wait_for_timeout(500)
        shot(page, "04-add-restaurant-form.png")

        # Close the form again — we'll use the cached ones
        page.get_by_role("button", name="Cancel").click()
        page.wait_for_timeout(300)

        # ── 5. Both restaurants selected — ready to review ───────────────────
        print("Step 5: Both restaurants selected")
        shot(page, "05-restaurants-selected.png")

        # ── 6. Click Review & Create Poll ────────────────────────────────────
        print("Step 6: Review & Create Poll page")
        page.get_by_role("button", name="Review & Create Poll").click()
        page.wait_for_timeout(800)
        shot(page, "06-menu-review.png")

        # Scroll down to see more of the menu
        page.evaluate("window.scrollBy(0, 400)")
        page.wait_for_timeout(300)
        shot(page, "07-menu-review-scrolled.png")

        # ── 7. Create the poll session ───────────────────────────────────────
        print("Step 7: Create poll")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(300)
        shot(page, "08-create-poll-button.png")
        # Click the "Create Poll (N items)" button
        page.get_by_role("button", name="Create Poll", exact=False).click()
        page.wait_for_timeout(1500)

        # ── 8. Poll link page ────────────────────────────────────────────────
        print("Step 8: Poll created — shareable link page")
        shot(page, "09-poll-link.png")

        # Extract the poll URL from the input field showing the session link
        poll_url_input = page.locator("input[readonly]").last
        poll_url = poll_url_input.input_value()
        if not poll_url.startswith("http"):
            poll_url = f"http://127.0.0.1:8766{poll_url}"
        print(f"  poll URL: {poll_url}")

        # ── 9. Open the poll page (simulate a team member opening it) ────────
        print("Step 9: Poll page — team member view")
        poll_page = ctx.new_page()
        poll_page.goto(poll_url, wait_until="domcontentloaded")
        poll_page.wait_for_selector("input[placeholder='Enter your name']", timeout=10000)
        poll_page.wait_for_timeout(600)
        shot(poll_page, "10-poll-page.png")

        # ── 10. Fill in name and select items ────────────────────────────────
        print("Step 10: Selecting items")
        poll_page.fill("input[placeholder='Enter your name']", "Jonathan")
        poll_page.wait_for_timeout(300)

        # Select a few checkboxes (FluentUI checkboxes use role="checkbox")
        checkboxes = poll_page.get_by_role("checkbox").all()
        for cb in checkboxes[:3]:
            cb.click()
            poll_page.wait_for_timeout(150)

        shot(poll_page, "11-order-selected.png")

        # ── 11. Submit order ─────────────────────────────────────────────────
        print("Step 11: Submit order")
        poll_page.get_by_role("button", name="Submit Order").click()
        poll_page.wait_for_timeout(1500)
        shot(poll_page, "12-order-submitted.png")

        # Scroll down to see order list
        poll_page.evaluate("window.scrollBy(0, 500)")
        poll_page.wait_for_timeout(400)
        shot(poll_page, "13-order-list.png")

        poll_page.close()
        browser.close()

    print("\nAll screenshots saved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=APP_URL)
    parser.add_argument("--password", default=APP_PASSWORD)
    args = parser.parse_args()
    run(args.url, args.password)
