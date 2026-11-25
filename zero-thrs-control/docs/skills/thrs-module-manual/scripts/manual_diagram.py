"""A manual's Mermaid diagram and the SVG rendered from it.

The manual keeps the Mermaid source as the thing to edit; manual_render.py renders
it to `<module>.svg` next to the manual, stamped with a hash of everything it was
rendered from, and the front-end shows the SVG in its place. A manual without a
Mermaid block, for a module without a state machine, has no SVG.
tests/manuals/test_published_manuals.py fails when a published SVG is out of date.
"""

import base64
import hashlib
import html
import io
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from playwright.sync_api import ViewportSize

SKILL = Path(__file__).parents[1]
REPOSITORY = SKILL.parents[3]
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@12.2.0/dist/mermaid.min.js"
MERMAID_SHA256 = "a8a6a6f805b074a8261a2825c86f99c8054acb3b35f50bb7e24a4f9f2c3c3b9f"
DIAGRAM_CSS = SKILL / "assets/diagram.css"
BASE_CSS = SKILL / "assets/base.css"
# The front-end's own font files, so labels are measured as the front-end draws them.
FONTS = REPOSITORY / "zero-ui/src/assets/fonts"
FONT_FILES = {
    ("Inter", "normal"): FONTS / "Inter/Inter-VariableFont_opsz,wght.ttf",
    ("Inter", "italic"): FONTS / "Inter/Inter-Italic-VariableFont_opsz,wght.ttf",
    ("Urbanist", "normal"): FONTS / "Urbanist/Urbanist-VariableFont_wght.ttf",
    ("Urbanist", "italic"): FONTS / "Urbanist/Urbanist-Italic-VariableFont_wght.ttf",
}
# Shipped inside the SVG, cut down to the diagram's characters, so it draws the same
# when opened as a file. Their own family names keep these partial fonts from
# replacing the front-end's full ones when the SVG is shown inside a page.
EMBEDDED_FONTS = {
    "Manual Diagram Inter": FONT_FILES[("Inter", "normal")],
    "Manual Diagram Urbanist": FONT_FILES[("Urbanist", "normal")],
}
SCREEN = ViewportSize(width=1280, height=900)

RENDER_DIAGRAM = """async ({ source, css }) => {
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    fontFamily: '"Manual Diagram Inter", Inter, sans-serif',
    themeCSS: css,
    // The default "neo" look strokes boxes with a fixed-colour gradient.
    look: "classic",
    state: { useMaxWidth: true },
    deterministicIds: true,
  });
  const { svg } = await mermaid.render("manual-diagram", source);
  // Mermaid returns HTML markup such as a bare <br>; a standalone .svg must be XML.
  const parsed = new DOMParser().parseFromString(svg, "text/html");
  return new XMLSerializer().serializeToString(parsed.querySelector("svg"));
}"""

MERMAID_BLOCK = re.compile(r'<pre class="mermaid">(.*?)</pre>', re.DOTALL)
DIAGRAM_HASH = re.compile(r'data-diagram-hash="(?P<hash>[0-9a-f]+)"')


def font_faces() -> str:
    return "\n".join(
        f'@font-face {{ font-family: "{family}"; font-style: {style}; font-weight: 100 900; '
        f"src: url(data:font/ttf;base64,{base64.b64encode(file.read_bytes()).decode()}); }}"
        for (family, style), file in FONT_FILES.items()
    )


def subset_font(file: Path, text: str) -> bytes:
    options = subset.Options()
    options.flavor = "woff"
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    font = subset.load_font(str(file), options)
    subsetter.subset(font)
    woff = io.BytesIO()
    subset.save_font(font, woff, options)
    return woff.getvalue()


def with_embedded_fonts(svg: str, source: str) -> str:
    text = html.unescape(source)
    faces = "".join(
        f'@font-face {{ font-family: "{family}"; font-weight: 100 900; '
        f"src: url(data:font/woff;base64,{base64.b64encode(subset_font(file, text)).decode()}); }}"
        for family, file in EMBEDDED_FONTS.items()
    )
    return re.sub(
        r"<svg[^>]*>", lambda tag: f"{tag[0]}<style>{faces}</style>", svg, count=1
    )


def missing_characters(labels: list[tuple[str, str]]) -> list[str]:
    """Each (font-family, text) label's characters that its embedded font lacks."""
    characters = {
        family: TTFont(file).getBestCmap().keys()
        for family, file in EMBEDDED_FONTS.items()
    }
    return sorted(
        {
            f"{character!r} in {text!r} ({family})"
            for font_family, text in labels
            for family in EMBEDDED_FONTS
            if font_family.startswith(f'"{family}"')
            for character in text
            if not character.isspace() and ord(character) not in characters[family]
        }
    )


def diagram_source(html: str) -> str | None:
    found = MERMAID_BLOCK.search(html)
    return None if found is None else found[1].strip()


def diagram_hash(source: str) -> str:
    rendered_from = hashlib.sha256()
    rendered_from.update(source.encode())
    rendered_from.update(MERMAID_SHA256.encode())
    rendered_from.update(RENDER_DIAGRAM.encode())
    rendered_from.update(f"{SCREEN['width']}x{SCREEN['height']}".encode())
    rendered_from.update(font_faces().encode())
    for path in (DIAGRAM_CSS, BASE_CSS):
        rendered_from.update(path.read_bytes())
    return rendered_from.hexdigest()[:16]


def verified_mermaid(script: bytes) -> str:
    if hashlib.sha256(script).hexdigest() != MERMAID_SHA256:
        raise SystemExit(
            f"{MERMAID} does not match MERMAID_SHA256; after upgrading Mermaid, "
            "set MERMAID_SHA256 to the new file's hash"
        )
    return script.decode()


def stamp_diagram(svg: str, source: str) -> str:
    return svg.replace("<svg ", f'<svg data-diagram-hash="{diagram_hash(source)}" ', 1)


def with_diagram(html: str, svg: str) -> str:
    return MERMAID_BLOCK.sub(lambda _: svg, html, count=1)


def diagram_path(manual: Path) -> Path:
    return manual.with_suffix(".svg")


def is_diagram_current(manual: Path) -> bool:
    source = diagram_source(manual.read_text())
    diagram = diagram_path(manual)
    if source is None:
        return not diagram.exists()
    if not diagram.exists():
        return False
    stamped = DIAGRAM_HASH.search(diagram.read_text())
    return stamped is not None and stamped["hash"] == diagram_hash(source)
