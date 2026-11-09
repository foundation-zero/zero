import importlib
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[2] / "docs/skills/thrs-module-manual/scripts"
MANUALS = Path(__file__).parents[3] / "zero-ui/src/modules/thrapp/documentation"


@pytest.fixture
def scripts(monkeypatch):
    monkeypatch.syspath_prepend(str(SCRIPTS))


@pytest.mark.parametrize(
    "manual", sorted(MANUALS.glob("*.html")), ids=lambda path: path.stem
)
def test_published_manual_matches_control_version(manual, scripts):
    manual_version = importlib.import_module("manual_version")
    module_facts = importlib.import_module("module_facts")

    module_name, stamped = manual_version.read_stamp(manual)
    current = module_facts.fingerprint(module_name)

    assert stamped == current, (
        f"{manual.name} describes control version {stamped}, but {module_name} is "
        f"now at {current}. Refresh it with the thrs-module-manual skill, or run "
        f"`just manual_stamp {module_name}` if it is still accurate."
    )


@pytest.mark.parametrize(
    "manual", sorted(MANUALS.glob("*.html")), ids=lambda path: path.stem
)
def test_published_diagram_matches_manual(manual, scripts):
    manual_diagram = importlib.import_module("manual_diagram")

    assert manual_diagram.is_diagram_current(manual), (
        f"{manual.stem}.svg is missing or was not rendered from {manual.name}'s Mermaid "
        f"source. Render it with `just manual {manual.stem}` and publish it with "
        f"`just manual_publish {manual.stem}`."
    )
