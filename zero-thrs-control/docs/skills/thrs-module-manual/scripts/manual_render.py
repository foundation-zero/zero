"""Render a manual's diagram, check it is current, or print the manual.

Run it from `zero-thrs-control`:

    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py diagram /tmp/thrs-manuals/dhw.html
    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py check /tmp/thrs-manuals/dhw.html
    uv run python docs/skills/thrs-module-manual/scripts/manual_render.py pdf /tmp/thrs-manuals/dhw.html

`diagram` counts the prose above Tuning and, when the manual has a Mermaid block,
writes `<module>.svg`, which the front-end shows in its place, and
`<module>-diagram.png` to look at. `check` fails when `<module>.svg` is out of
date, or exists for a manual without a Mermaid block. `pdf` prints `<module>.pdf`
from the manual and its SVG.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from html import escape
from pathlib import Path
from typing import Annotated

from manual_diagram import (
    BASE_CSS,
    DIAGRAM_CSS,
    MERMAID,
    RENDER_DIAGRAM,
    SCREEN,
    SKILL,
    diagram_path,
    diagram_source,
    font_faces,
    is_diagram_current,
    missing_characters,
    stamp_diagram,
    verified_mermaid,
    with_diagram,
    with_embedded_fonts,
)
from playwright.sync_api import Browser, Page, ViewportSize, sync_playwright
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, CliApp, CliPositionalArg, CliSubCommand

PRINT_CSS = SKILL / "assets/print.css"
PROSE_WORD_LIMIT = 425
PAGE_MARGIN = "18mm"
# A4 is 210 x 297 mm; at the CSS 96 dpi that leaves this much inside the margins.
PRINTABLE = ViewportSize(width=658, height=986)
# The front-end's colour variables diagram.css may use; any other colour in the SVG
# would ignore the front-end's theme.
THEME_VARIABLES = ["--background", "--foreground", "--muted-foreground", "--border"]

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
    return ["fill", "stroke", "color", "backgroundColor", "filter"]
      .filter((property) => !themed.has(style[property]))
      .map((property) => `<${element.tagName} class="${element.getAttribute("class") ?? ""}"> ${property}: ${style[property]}`);
  });
  sentinels.remove();
  return [...new Set(unthemed)];
}"""

LABEL_FONTS = """() => {
  const labels = document.createTreeWalker(
    document.querySelector("#manual-diagram"),
    NodeFilter.SHOW_TEXT,
  );
  const found = [];
  for (let text = labels.nextNode(); text; text = labels.nextNode()) {
    if (text.textContent.trim() && !text.parentElement.closest("style")) {
      found.push([getComputedStyle(text.parentElement).fontFamily, text.textContent]);
    }
  }
  return found;
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


def render_manual(manual: Path) -> None:
    html = manual.read_text()
    source = diagram_source(html)

    with chromium() as browser:
        page = open_manual(browser, html, SCREEN)
        prose_words = page.evaluate(COUNT_PROSE_WORDS)
        if source is None:
            diagram_path(manual).unlink(missing_ok=True)
            print(f'{manual.name} has no <pre class="mermaid"> diagram to render')
        else:
            render_diagram(page, manual, source)

    print(
        f"Prose above Tuning: {prose_words} of {PROSE_WORD_LIMIT} words"
        + (" — too long, cut the prose" if prose_words > PROSE_WORD_LIMIT else "")
    )


def render_diagram(page: Page, manual: Path, source: str) -> None:
    preview = manual.with_name(f"{manual.stem}-diagram.png")
    page.add_script_tag(content=verified_mermaid(page.request.get(MERMAID).body()))
    svg = page.evaluate(
        RENDER_DIAGRAM, {"source": source, "css": DIAGRAM_CSS.read_text()}
    )
    page.evaluate(
        "(svg) => { document.querySelector('pre.mermaid').outerHTML = svg; }", svg
    )
    unthemed = page.evaluate(UNTHEMED_COLOURS, THEME_VARIABLES)
    missing = missing_characters(page.evaluate(LABEL_FONTS))
    page.locator("#manual-diagram").screenshot(path=preview)

    if unthemed:
        raise SystemExit(
            "These colours come from Mermaid's theme, not the front-end's, so they would "
            f"not follow dark mode; restyle them in {DIAGRAM_CSS.name}:\n  "
            + "\n  ".join(unthemed)
        )
    if missing:
        raise SystemExit(
            "These characters are not in the diagram's fonts, so they would be drawn "
            "in a fallback font and overflow their box; rephrase them:\n  "
            + "\n  ".join(missing)
        )
    diagram = diagram_path(manual)
    diagram.write_text(stamp_diagram(with_embedded_fonts(svg, source), source))
    print(f"Wrote {diagram} and {preview}")


def footer(title: str, version: str) -> str:
    return f"""
      <div style="width: 100%; padding: 0 {PAGE_MARGIN}; display: flex; justify-content: space-between;
                  font-family: Inter, sans-serif; font-size: 8px; color: #6b7280;">
        <span>{escape(title)}</span>
        <span>{escape(version)}</span>
        <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
      </div>"""


def print_manual(manual: Path) -> None:
    diagram = diagram_path(manual)
    html = (
        with_diagram(manual.read_text(), diagram.read_text())
        if diagram.exists()
        else manual.read_text()
    )
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
            f"{diagram_path(manual).name} does not match {manual.name}'s Mermaid "
            f"block; render it with `just manual {manual.stem}`"
        )


class ManualArgument(BaseModel):
    manual: Annotated[
        CliPositionalArg[Path], Field(description="The manual's HTML fragment")
    ]


class DiagramCmd(ManualArgument):
    """Count the manual's prose and render its diagram, if any, to <module>.svg."""

    def cli_cmd(self) -> None:
        render_manual(self.manual)


class CheckCmd(ManualArgument):
    """Fail when <module>.svg does not match the manual's Mermaid block, or its absence."""

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
