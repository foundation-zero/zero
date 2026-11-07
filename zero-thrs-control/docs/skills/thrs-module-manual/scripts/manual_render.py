"""Render a manual's diagram, or print the manual, in headless Chromium.

Run it from `zero-thrs-control`:

    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py diagram /tmp/thrs-manuals/dhw.html
    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py pdf /tmp/thrs-manuals/dhw.html

`diagram` writes `<module>.svg`, which the front-end shows in place of the Mermaid
source, and `<module>-diagram.png` to look at, and counts the prose above Tuning.
`pdf` prints `<module>.pdf` from the manual and that SVG.
"""

import argparse
import base64
from html import escape
from pathlib import Path

from manual_diagram import (
    DIAGRAM_CSS,
    diagram_path,
    diagram_source,
    stamp_diagram,
    with_diagram,
)
from playwright.sync_api import Browser, Page, sync_playwright

MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@12.2.0/dist/mermaid.min.js"
ASSETS = Path(__file__).parents[1] / "assets"
# The front-end's own font files, so labels are measured as the front-end draws them.
FONTS = Path(__file__).parents[5] / "zero-ui/src/assets/fonts"
FONT_FILES = {
    ("Inter", "normal"): "Inter/Inter-VariableFont_opsz,wght.ttf",
    ("Inter", "italic"): "Inter/Inter-Italic-VariableFont_opsz,wght.ttf",
    ("Urbanist", "normal"): "Urbanist/Urbanist-VariableFont_wght.ttf",
    ("Urbanist", "italic"): "Urbanist/Urbanist-Italic-VariableFont_wght.ttf",
}
PROSE_WORD_LIMIT = 425
PAGE_MARGIN = "18mm"
# A4 is 210 × 297 mm; at the CSS 96 dpi that leaves this much inside the margins.
PRINTABLE = {"width": 658, "height": 986}
SCREEN = {"width": 1280, "height": 900}

RENDER_DIAGRAM = """async ({ source, css }) => {
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    fontFamily: "Inter, sans-serif",
    themeCSS: css,
    state: { useMaxWidth: true },
    deterministicIds: true,
  });
  const { svg } = await mermaid.render("manual-diagram", source);
  return svg;
}"""

COUNT_PROSE_WORDS = """() => {
  const tuning = document.querySelector("#tuning");
  const prose = document.createRange();
  prose.setStartBefore(tuning.parentElement.firstChild);
  prose.setEndBefore(tuning);
  const fragment = prose.cloneContents();
  fragment.querySelectorAll("figure").forEach((figure) => figure.remove());
  return fragment.textContent.split(/\\s+/).filter(Boolean).length;
}"""


def font_faces() -> str:
    return "\n".join(
        f'@font-face {{ font-family: "{family}"; font-style: {style}; font-weight: 100 900; '
        f"src: url(data:font/ttf;base64,{base64.b64encode((FONTS / file).read_bytes()).decode()}); }}"
        for (family, style), file in FONT_FILES.items()
    )


def open_manual(browser: Browser, html: str, viewport: dict, *stylesheets: str) -> Page:
    css = "\n".join(
        [
            font_faces(),
            *((ASSETS / name).read_text() for name in ("base.css", *stylesheets)),
        ]
    )
    page = browser.new_page(viewport=viewport)
    page.set_content(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{css}</style></head>'
        f'<body><article class="manual">{html}</article></body></html>'
    )
    page.evaluate("Promise.all([...document.fonts].map((font) => font.load()))")
    return page


def render_diagram(manual: Path) -> None:
    html = manual.read_text()
    source = diagram_source(html)
    if source is None:
        raise SystemExit(f'{manual.name} has no <pre class="mermaid"> diagram')

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = open_manual(browser, html, SCREEN)
        prose_words = page.evaluate(COUNT_PROSE_WORDS)
        page.add_script_tag(url=MERMAID)
        svg = page.evaluate(
            RENDER_DIAGRAM,
            {"source": source, "css": DIAGRAM_CSS.read_text()},
        )
        page.evaluate(
            "(svg) => { document.querySelector('pre.mermaid').outerHTML = svg; }", svg
        )
        preview = manual.with_name(f"{manual.stem}-diagram.png")
        page.locator("#manual-diagram").screenshot(path=preview)
        browser.close()

    diagram = diagram_path(manual)
    diagram.write_text(stamp_diagram(svg, source))
    print(f"Wrote {diagram} and {preview}")
    print(
        f"Prose above Tuning: {prose_words} of {PROSE_WORD_LIMIT} words"
        + (" — too long, cut the prose" if prose_words > PROSE_WORD_LIMIT else "")
    )


def footer(title: str, version: str) -> str:
    return f"""
      <div style="width: 100%; padding: 0 {PAGE_MARGIN}; display: flex; justify-content: space-between;
                  font-family: Inter, sans-serif; font-size: 8px; color: #6b7280;">
        <span>{escape(title)}</span>
        <span>{escape(version)}</span>
        <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
      </div>"""


def print_manual(manual: Path) -> None:
    html = with_diagram(manual.read_text(), diagram_path(manual).read_text())
    pdf = manual.with_suffix(".pdf")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = open_manual(browser, html, PRINTABLE, "print.css")
        page.emulate_media(media="print", color_scheme="light")
        title = page.text_content("h1") or ""
        version = (page.text_content("p.version") or "").strip()
        page.pdf(
            path=pdf,
            prefer_css_page_size=True,
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=footer(title, version),
        )
        browser.close()

    print(f"Wrote {pdf}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", choices=["diagram", "pdf"])
    parser.add_argument("manual", type=Path)
    args = parser.parse_args()
    if args.output == "diagram":
        render_diagram(args.manual)
    else:
        print_manual(args.manual)


if __name__ == "__main__":
    main()
