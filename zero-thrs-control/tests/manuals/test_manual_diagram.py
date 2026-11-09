import importlib
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[2] / "docs/skills/thrs-module-manual/scripts"
SOURCE = "stateDiagram-v2\n  [*] --> idle"
SVG = '<svg id="manual-diagram" width="100%"><g></g></svg>'


@pytest.fixture
def manual_diagram(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))
    return importlib.import_module("manual_diagram")


def manual(source: str) -> str:
    return f'<h2>Boosting</h2><figure class="diagram"><pre class="mermaid">\n{source}\n</pre></figure>'


def test_diagram_source_is_the_trimmed_mermaid_block(manual_diagram):
    assert manual_diagram.diagram_source(manual(SOURCE)) == SOURCE
    assert manual_diagram.diagram_source("<h2>Tuning</h2>") is None


def test_with_diagram_replaces_the_mermaid_block(manual_diagram):
    assert manual_diagram.with_diagram(manual(SOURCE), r"<svg>\1</svg>") == (
        r'<h2>Boosting</h2><figure class="diagram"><svg>\1</svg></figure>'
    )


@pytest.mark.parametrize(
    ("rendered_from", "current"),
    [(SOURCE, True), (f"{SOURCE}\n  idle --> busy", False)],
)
def test_diagram_is_current_only_when_rendered_from_the_manual(
    manual_diagram, tmp_path, rendered_from, current
):
    page = tmp_path / "dhw.html"
    page.write_text(manual(SOURCE))
    (tmp_path / "dhw.svg").write_text(manual_diagram.stamp_diagram(SVG, rendered_from))

    assert manual_diagram.is_diagram_current(page) is current


def test_diagram_is_not_current_when_missing_or_unstamped(manual_diagram, tmp_path):
    page = tmp_path / "dhw.html"
    page.write_text(manual(SOURCE))
    assert not manual_diagram.is_diagram_current(page)

    (tmp_path / "dhw.svg").write_text(SVG)
    assert not manual_diagram.is_diagram_current(page)


@pytest.mark.parametrize("stylesheet_name", ["DIAGRAM_CSS", "BASE_CSS"])
def test_diagram_is_not_current_after_a_stylesheet_change(
    manual_diagram, tmp_path, monkeypatch, stylesheet_name
):
    stylesheet = tmp_path / "stylesheet.css"
    stylesheet.write_text(".node rect { rx: 12px; }")
    monkeypatch.setattr(manual_diagram, stylesheet_name, stylesheet)
    page = tmp_path / "dhw.html"
    page.write_text(manual(SOURCE))
    (tmp_path / "dhw.svg").write_text(manual_diagram.stamp_diagram(SVG, SOURCE))

    stylesheet.write_text(".node rect { rx: 4px; }")

    assert not manual_diagram.is_diagram_current(page)


def test_diagram_is_not_current_after_a_mermaid_upgrade(
    manual_diagram, tmp_path, monkeypatch
):
    page = tmp_path / "dhw.html"
    page.write_text(manual(SOURCE))
    (tmp_path / "dhw.svg").write_text(manual_diagram.stamp_diagram(SVG, SOURCE))

    monkeypatch.setattr(manual_diagram, "MERMAID", "https://cdn.example/mermaid@13.0.0")

    assert not manual_diagram.is_diagram_current(page)
