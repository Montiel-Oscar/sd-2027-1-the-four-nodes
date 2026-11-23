"""Exporta las slides locales a PDF sin servicios externos; requiere playwright y Edge."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    root = Path(__file__).resolve().parent
    with sync_playwright() as playwright:
        executable = os.getenv("PLAYWRIGHT_BROWSER")
        browser = playwright.chromium.launch(executable_path=executable, headless=True) if executable else playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width":1440,"height":1000})
        page.goto((root / "diapositivas.html").as_uri())
        assert page.locator("section").count() == 7
        for width in (390, 1440):
            page.set_viewport_size({"width":width,"height":1000})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.set_viewport_size({"width":1440,"height":1000})
        page.keyboard.press("ArrowRight")
        assert page.locator("#position").inner_text() == "2 / 7"
        page.keyboard.press("Home")
        page.pdf(path=str(root / "diapositivas.pdf"), prefer_css_page_size=True, print_background=True)
        browser.close()
    print("PDF exportado: docs/pitch/diapositivas.pdf")


if __name__ == "__main__":
    main()
