"""A manual's Mermaid diagram and the SVG rendered from it.

The manual keeps the Mermaid source as the thing to edit; manual_render.py renders
it to `<module>.svg` next to the manual, stamped with a hash of that source and of
the diagram stylesheet, and the front-end shows the SVG in its place.
tests/manuals/test_published_manuals.py fails when a published SVG no longer
matches either.
"""

import hashlib
import re
from pathlib import Path

MERMAID_BLOCK = re.compile(r'<pre class="mermaid">(.*?)</pre>', re.DOTALL)
SOURCE_HASH = re.compile(r'data-source-hash="(?P<hash>[0-9a-f]+)"')
DIAGRAM_CSS = Path(__file__).parents[1] / "assets/diagram.css"


def diagram_source(html: str) -> str | None:
    found = MERMAID_BLOCK.search(html)
    return None if found is None else found[1].strip()


def source_hash(source: str) -> str:
    rendered_from = f"{source}\n{DIAGRAM_CSS.read_text()}"
    return hashlib.sha256(rendered_from.encode()).hexdigest()[:16]


def stamp_diagram(svg: str, source: str) -> str:
    return svg.replace("<svg ", f'<svg data-source-hash="{source_hash(source)}" ', 1)


def with_diagram(html: str, svg: str) -> str:
    return MERMAID_BLOCK.sub(lambda _: svg, html, count=1)


def diagram_path(manual: Path) -> Path:
    return manual.with_suffix(".svg")


def is_diagram_current(manual: Path) -> bool:
    source = diagram_source(manual.read_text())
    diagram = diagram_path(manual)
    if source is None or not diagram.exists():
        return False
    stamped = SOURCE_HASH.search(diagram.read_text())
    return stamped is not None and stamped["hash"] == source_hash(source)
