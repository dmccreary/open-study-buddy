#!/usr/bin/env python3
"""Refresh the QR code in one-pager.html and render one-pager.pdf (US Letter).

Requires: pip install segno playwright   (uses the installed Google Chrome)
Usage:    python3 media/handouts/build-pdf.py
"""
import io
import re
from pathlib import Path

import segno
from playwright.sync_api import sync_playwright

URL = "https://dmccreary.github.io/open-study-buddy/"
HERE = Path(__file__).resolve().parent
HTML = HERE / "one-pager.html"
PDF = HERE / "one-pager.pdf"


def qr_svg() -> str:
    buf = io.BytesIO()
    segno.make(URL, error="m").save(
        buf, kind="svg", scale=1, border=1, xmldecl=False, svgns=True,
        dark="#14325c", light="#ffffff", omitsize=True, lineclass=None,
    )
    return buf.getvalue().decode()


def inject_qr() -> None:
    text = HTML.read_text()
    block = f"<!--QR-->{qr_svg()}<!--/QR-->"
    if "<!--/QR-->" in text:
        text = re.sub(r"<!--QR-->.*?<!--/QR-->", lambda m: block, text, flags=re.S)
    else:
        text = text.replace("<!--QR-->", block, 1)
    HTML.write_text(text)


def render_pdf() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page()
        page.goto(HTML.as_uri())
        page.wait_for_load_state("networkidle")
        page.pdf(path=str(PDF), width="8.5in", height="11in",
                 print_background=True, prefer_css_page_size=True)
        browser.close()


if __name__ == "__main__":
    inject_qr()
    render_pdf()
    print(f"Wrote {PDF}")
