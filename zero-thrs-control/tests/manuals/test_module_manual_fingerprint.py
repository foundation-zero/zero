import importlib.util
from pathlib import Path

import pytest

from thrs.control.modules import dhw, pvt_group

MODULE_FACTS = (
    Path(__file__).parents[2] / "docs/skills/thrs-module-manual/scripts/module_facts.py"
)


@pytest.fixture
def module_facts():
    spec = importlib.util.spec_from_file_location("module_facts", MODULE_FACTS)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def edit_source(monkeypatch, tmp_path):
    def edit(module, old: str, new: str):
        source = Path(module.__file__).read_text()
        assert old in source
        edited = tmp_path / Path(module.__file__).name
        edited.write_text(source.replace(old, new))
        monkeypatch.setattr(module, "__file__", str(edited))

    return edit


def test_fingerprint_is_stable(module_facts):
    assert module_facts.fingerprint("dhw") == module_facts.fingerprint("dhw")


def test_changed_constant_of_a_sub_control_changes_fingerprint(
    module_facts, edit_source
):
    before = module_facts.fingerprint("pvt")

    edit_source(
        pvt_group,
        "RECOVERY_MIX_UPPER_BOUND: Ratio = 0.2",
        "RECOVERY_MIX_UPPER_BOUND: Ratio = 0.4",
    )

    assert module_facts.fingerprint("pvt") != before


def test_changed_control_loop_check_changes_fingerprint(module_facts, edit_source):
    before = module_facts.fingerprint("dhw")

    edit_source(
        dhw,
        "shortfall.total_seconds() < self._parameters.boosting_stall_window",
        "shortfall.total_seconds() <= self._parameters.boosting_stall_window",
    )

    assert module_facts.fingerprint("dhw") != before


def test_changed_helper_class_changes_fingerprint(module_facts, edit_source):
    before = module_facts.fingerprint("dhw")

    edit_source(dhw, "and tank.enabled\n", "")

    assert module_facts.fingerprint("dhw") != before
