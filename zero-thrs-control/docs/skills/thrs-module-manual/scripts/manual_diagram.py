"""A manual's Mermaid diagram and the SVG rendered from it.

The manual keeps the Mermaid source as the thing to edit; manual_render.py renders
it to `<module>.svg` next to the manual, stamped with a hash of everything it was
rendered from, and the front-end shows the SVG in its place.
tests/manuals/test_published_manuals.py fails when a published SVG is out of date.
"""

import hashlib
import re
from pathlib import Path

SKILL = Path(__file__).parents[1]
REPOSITORY = SKILL.parents[3]
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@12.2.0/dist/mermaid.min.js"
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

MERMAID_BLOCK = re.compile(r'<pre class="mermaid">(.*?)</pre>', re.DOTALL)
DIAGRAM_HASH = re.compile(r'data-diagram-hash="(?P<hash>[0-9a-f]+)"')


def diagram_source(html: str) -> str | None:
    found = MERMAID_BLOCK.search(html)
    return None if found is None else found[1].strip()


def diagram_hash(source: str) -> str:
    rendered_from = hashlib.sha256()
    rendered_from.update(source.encode())
    rendered_from.update(MERMAID.encode())
    for path in (DIAGRAM_CSS, BASE_CSS, *FONT_FILES.values()):
        rendered_from.update(path.read_bytes())
    return rendered_from.hexdigest()[:16]


def stamp_diagram(svg: str, source: str) -> str:
    return svg.replace("<svg ", f'<svg data-diagram-hash="{diagram_hash(source)}" ', 1)


def with_diagram(html: str, svg: str) -> str:
    return MERMAID_BLOCK.sub(lambda _: svg, html, count=1)


def diagram_path(manual: Path) -> Path:
    return manual.with_suffix(".svg")


def is_diagram_current(manual: Path) -> bool:
    source = diagram_source(manual.read_text())
    diagram = diagram_path(manual)
    if source is None or not diagram.exists():
        return False
    stamped = DIAGRAM_HASH.search(diagram.read_text())
    return stamped is not None and stamped["hash"] == diagram_hash(source)
