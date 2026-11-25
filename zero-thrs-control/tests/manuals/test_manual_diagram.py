import base64
import hashlib
import importlib
import io
import re
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

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


def test_manual_without_a_diagram_is_current_only_without_an_svg(
    manual_diagram, tmp_path
):
    page = tmp_path / "dc.html"
    page.write_text("<h2>How it regulates</h2>")
    assert manual_diagram.is_diagram_current(page)

    (tmp_path / "dc.svg").write_text(manual_diagram.stamp_diagram(SVG, SOURCE))
    assert not manual_diagram.is_diagram_current(page)


def test_verified_mermaid_rejects_any_other_script(manual_diagram, monkeypatch):
    script = b"window.mermaid = {};"
    monkeypatch.setattr(
        manual_diagram, "MERMAID_SHA256", hashlib.sha256(script).hexdigest()
    )

    assert manual_diagram.verified_mermaid(script) == "window.mermaid = {};"
    with pytest.raises(SystemExit):
        manual_diagram.verified_mermaid(b"window.mermaid = null;")


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


@pytest.mark.parametrize(
    ("setting", "changed"),
    [
        ("MERMAID_SHA256", "0" * 64),
        ("RENDER_DIAGRAM", 'async ({ source }) => mermaid.render("d", source)'),
        ("SCREEN", {"width": 1024, "height": 900}),
    ],
)
def test_diagram_is_not_current_after_a_renderer_change(
    manual_diagram, tmp_path, monkeypatch, setting, changed
):
    page = tmp_path / "dhw.html"
    page.write_text(manual(SOURCE))
    (tmp_path / "dhw.svg").write_text(manual_diagram.stamp_diagram(SVG, SOURCE))

    monkeypatch.setattr(manual_diagram, setting, changed)

    assert not manual_diagram.is_diagram_current(page)


def test_diagram_is_not_current_after_a_font_family_change(
    manual_diagram, tmp_path, monkeypatch
):
    page = tmp_path / "dhw.html"
    page.write_text(manual(SOURCE))
    (tmp_path / "dhw.svg").write_text(manual_diagram.stamp_diagram(SVG, SOURCE))

    monkeypatch.setattr(
        manual_diagram,
        "FONT_FILES",
        {
            ("Roboto", style): file
            for (_, style), file in manual_diagram.FONT_FILES.items()
        },
    )

    assert not manual_diagram.is_diagram_current(page)


def test_missing_characters_are_those_the_label_font_lacks(manual_diagram):
    labels = [
        ('"Manual Diagram Urbanist", Urbanist, sans-serif', "Boosting Δ"),
        ('"Manual Diagram Inter", Inter, sans-serif', "Δ ≥ 5 °C"),
    ]

    assert manual_diagram.missing_characters(labels) == [
        "'Δ' in 'Boosting Δ' (Manual Diagram Urbanist)"
    ]


def test_embedded_fonts_cover_every_character_of_the_diagram(manual_diagram):
    source = "stateDiagram-v2\n  idle --> boosting: supply &gt; 5 °C"

    svg = manual_diagram.with_embedded_fonts(SVG, source)

    fonts = re.findall(r"base64,([A-Za-z0-9+/=]+)", svg)
    assert svg.startswith('<svg id="manual-diagram" width="100%"><style>@font-face')
    assert len(fonts) == len(manual_diagram.EMBEDDED_FONTS)
    for font in fonts:
        characters = TTFont(io.BytesIO(base64.b64decode(font))).getBestCmap()
        assert set(map(ord, "idle--> boosting: supply > 5 °C")) <= characters.keys()
