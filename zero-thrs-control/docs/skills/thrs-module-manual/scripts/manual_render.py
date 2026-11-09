"""Render a manual's diagram, check it is current, or print the manual.

Run it from `zero-thrs-control`:

    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py diagram /tmp/thrs-manuals/dhw.html
    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py check /tmp/thrs-manuals/dhw.html
    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py pdf /tmp/thrs-manuals/dhw.html

`diagram` writes `<module>.svg`, which the front-end shows in place of the Mermaid
source, and `<module>-diagram.png` to look at, and counts the prose above Tuning.
`check` fails when `<module>.svg` is out of date. `pdf` prints `<module>.pdf` from
the manual and that SVG.
"""

import base64
from collections.abc import Iterator
from contextlib import contextmanager
from html import escape
from pathlib import Path
from typing import Annotated

from manual_diagram import (
    BASE_CSS,
    DIAGRAM_CSS,
    FONT_FILES,
    MERMAID,
    SKILL,
    diagram_path,
    diagram_source,
    is_diagram_current,
    stamp_diagram,
    with_diagram,
)
from playwright.sync_api import Browser, Page, ViewportSize, sync_playwright
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, CliApp, CliPositionalArg, CliSubCommand

PRINT_CSS = SKILL / "assets/print.css"
PROSE_WORD_LIMIT = 425
PAGE_MARGIN = "18mm"
# A4 is 210 x 297 mm; at the CSS 96 dpi that leaves this much inside the margins.
PRINTABLE = ViewportSize(width=658, height=986)
SCREEN = ViewportSize(width=1280, height=900)
# The front-end's colour variables diagram.css may use; any other colour in the SVG
# would ignore the front-end's theme.
THEME_VARIABLES = ["--background", "--foreground", "--muted-foreground", "--border"]

RENDER_DIAGRAM = """async ({ source, css }) => {
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    fontFamily: "Inter, sans-serif",
    themeCSS: css,
    // The default "neo" look strokes boxes with a fixed-colour gradient.
    look: "classic",
    state: { useMaxWidth: true },
    deterministicIds: true,
  });
  const { svg } = await mermaid.render("manual-diagram", source);
  return svg;
}"""

UNTHEMED_COLOURS = """(variables) => {
  const sentinels = document.createElement("style");
  sentinels.textContent = `:root { ${variables
    .map((name, index) => `${name}: rgb(${index + 1}, 2, 3);`)
    .join(" ")} } body { color: var(--foreground); }`;
  document.head.append(sentinels);
  const themed = new Set(["none", "rgba(0, 0, 0, 0)"]);
  variables.forEach((_, index) => themed.add(`rgb(${index + 1}, 2, 3)`));
  const svg = document.querySelector("#manual-diagram");
  const unthemed = [svg, ...svg.querySelectorAll("*")].flatMap((element) => {
    const style = getComputedStyle(element);
    return ["fill", "stroke", "color", "backgroundColor"]
      .filter((property) => !themed.has(style[property]))
      .map((property) => `<${element.tagName} class="${element.getAttribute("class") ?? ""}"> ${property}: ${style[property]}`);
  });
  sentinels.remove();
  return [...new Set(unthemed)];
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
        f"src: url(data:font/ttf;base64,{base64.b64encode(file.read_bytes()).decode()}); }}"
        for (family, style), file in FONT_FILES.items()
    )


@contextmanager
def chromium() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            yield browser
        finally:
            browser.close()


def open_manual(
    browser: Browser, html: str, viewport: ViewportSize, *stylesheets: Path
) -> Page:
    css = "\n".join(
        [font_faces(), *(sheet.read_text() for sheet in (BASE_CSS, *stylesheets))]
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
    preview = manual.with_name(f"{manual.stem}-diagram.png")

    with chromium() as browser:
        page = open_manual(browser, html, SCREEN)
        prose_words = page.evaluate(COUNT_PROSE_WORDS)
        page.add_script_tag(url=MERMAID)
        svg = page.evaluate(
            RENDER_DIAGRAM, {"source": source, "css": DIAGRAM_CSS.read_text()}
        )
        page.evaluate(
            "(svg) => { document.querySelector('pre.mermaid').outerHTML = svg; }", svg
        )
        unthemed = page.evaluate(UNTHEMED_COLOURS, THEME_VARIABLES)
        page.locator("#manual-diagram").screenshot(path=preview)

    if unthemed:
        raise SystemExit(
            "These colours come from Mermaid's theme, not the front-end's, so they would "
            f"not follow dark mode; restyle them in {DIAGRAM_CSS.name}:\n  "
            + "\n  ".join(unthemed)
        )
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

    with chromium() as browser:
        page = open_manual(browser, html, PRINTABLE, PRINT_CSS)
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

    print(f"Wrote {pdf}")


def check_diagram(manual: Path) -> None:
    if not is_diagram_current(manual):
        raise SystemExit(
            f"{diagram_path(manual).name} is missing or out of date; "
            f"render it with `just manual {manual.stem}`"
        )


class ManualArgument(BaseModel):
    manual: Annotated[
        CliPositionalArg[Path], Field(description="The manual's HTML fragment")
    ]


class DiagramCmd(ManualArgument):
    """Render the manual's diagram to <module>.svg and count its prose."""

    def cli_cmd(self) -> None:
        render_diagram(self.manual)


class CheckCmd(ManualArgument):
    """Fail when <module>.svg was not rendered from the manual as it is now."""

    def cli_cmd(self) -> None:
        check_diagram(self.manual)


class PdfCmd(ManualArgument):
    """Print the manual and its diagram to <module>.pdf."""

    def cli_cmd(self) -> None:
        print_manual(self.manual)


class ManualRenderCli(BaseSettings, cli_kebab_case=True):
    diagram: CliSubCommand[DiagramCmd]
    check: CliSubCommand[CheckCmd]
    pdf: CliSubCommand[PdfCmd]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)


if __name__ == "__main__":
    CliApp.run(ManualRenderCli)
