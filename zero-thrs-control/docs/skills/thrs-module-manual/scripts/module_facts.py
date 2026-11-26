"""Dump the documentable facts of a thrs control module.

Everything here is read from the live objects rather than from the source text,
so the output cannot drift from the code the way a hand-read summary can. Run it
from `zero-thrs-control` with `uv run python <this file> <module>`.

    uv run python docs/skills/thrs-module-manual/scripts/module_facts.py pcm
    uv run python ... pcm --diagram /tmp/pcm_truth.mmd

`--diagram` writes python-statemachine's raw Mermaid rendering of the state
machine. That picture is the ground truth to check a redrawn figure against; it is
too dense to ship in a manual.
"""

import argparse
import contextlib
import hashlib
import importlib
import inspect
import io
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

from statemachine import StateChart

from thrs.input_output.definitions.units import unit_meta

# Display units for the `modelica_name` carried by each unit alias in
# thrs.input_output.definitions.units.
UNITS: dict[str, str] = {
    "C": "°C",
    "K": "K",
    "l_min": "l/min",
    "ratio": "0\u20131",
    "Bar": "bar",
    "Watt": "W",
    "s": "s",
    "Joule": "J",
    "Liter": "L",
    "Hz": "Hz",
    "Degree": "°",
    "bool": "on/off",
}


def bounds_of(metadata: list[Any]) -> list[str]:
    out: list[str] = []
    for m in metadata:
        for attr, symbol in (("ge", "≥"), ("gt", ">"), ("le", "≤"), ("lt", "<")):
            value = getattr(m, attr, None)
            if value is None:
                continue
            out.append(f"{symbol} {value}")
    return out


def describe_parameters(parameters_cls: type) -> None:
    print("## Parameters\n")
    print("Each line: name | unit | default | bounds | description in the code")
    for name, field in parameters_cls.model_fields.items():
        meta = unit_meta(field.annotation)
        unit = meta.modelica_name if meta else None
        display = UNITS.get(unit or "", unit or "")
        default = field.default
        if isinstance(default, tuple) and len(default) == 3:
            display = display or "PID (Kp, Ki, Kd)"
        bounds = ", ".join(bounds_of(field.metadata)) or "-"
        print(
            f"- {name} | {display or '-'} | {default!r} | {bounds} | "
            f"{field.description or '(none)'}"
        )
    print()

    validators = [
        member
        for name, member in inspect.getmembers(parameters_cls, inspect.isfunction)
        if getattr(member, "__pydantic_validator_info__", None)
        or name.startswith("check_")
    ]
    if validators:
        print("### Cross-parameter rules (model validators)\n")
        print("These reject a parameter set outright — they are hard constraints.\n")
        for fn in validators:
            try:
                print(inspect.getsource(fn).rstrip())
            except OSError:
                print(f"    {fn.__name__}")
        print()


def describe_alarms(alarms: Any) -> None:
    print("## Alarms\n")
    checks = [
        member
        for _, member in inspect.getmembers(
            alarms, lambda f: hasattr(f, "__alarm_code__")
        )
    ]
    if not checks:
        print("(this module defines no alarms)\n")
        return
    print("Each line: code | severity | condition that raises it\n")
    for check in checks:
        severity = "?"
        try:
            body = inspect.getsource(check)
            if "Severity." in body:
                severity = body.split("Severity.")[1].split(")")[0].split(",")[0]
        except OSError:
            body = ""
        print(f"- {check.__alarm_code__} | {severity} | via {check.__name__}")
    print()


def describe_modes(description: Any, control: Any) -> None:
    """The mode is what the operator sees on the panel as 'what the control is doing'.

    A module can report several independent mode dimensions, and not all of them
    come from a state machine — DHW derives its filling mode from the tank
    controller — so the `mode` property is printed too.
    """
    print("## Control modes (what the operator sees)\n")
    print("Mode dimensions reported by this module:\n")
    for name in type(control.mode).model_fields:
        print(f"- {name}")
    print()
    print("### `mode`\n")
    print(inspect.getsource(type(control).mode.fget).rstrip())
    print()


def describe_io(description: Any) -> None:
    for label, cls in (
        ("Actuators it drives (control values)", description.control_values_cls),
        ("Sensors it reads (sensor values)", description.sensor_values_cls),
    ):
        print(f"## {label}\n")
        for name, field in cls.model_fields.items():
            kind = getattr(field.annotation, "__name__", str(field.annotation))
            print(f"- {name} ({kind})")
        print()


def state_machines(control: Any) -> list[tuple[str, Any]]:
    """The control's own state machine and those of its sub-controls, labelled."""
    subs = []
    for attr in sorted(dir(control)):
        if attr.startswith("__"):
            continue
        sub = inspect.getattr_static(control, attr)
        sub_machine = getattr(sub, "_state_machine", None)
        if isinstance(sub, StateChart):
            label = "top level" if sub.model is control else f"sub-control `{attr}`"
            subs.append((label, sub))
        elif sub is not control and isinstance(sub_machine, StateChart):
            subs.append((f"sub-control `{attr}`", sub_machine))
    return list({id(sub): (label, sub) for label, sub in subs}.values())


def describe_state_machines(control: Any) -> None:
    print("## State machine(s)\n")
    machines = state_machines(control)
    for label, machine in machines:
        print(f"### {label} — {type(machine).__name__}\n")
        print(f"```mermaid\n{machine:mermaid}\n```\n")

    if not machines:
        print(
            "(no state machine — this module is continuous control only, so the "
            "manual needs a different figure, or none)\n"
        )


def write_diagram(control: Any, path: str) -> None:
    machines = state_machines(control)
    if not machines:
        print("\nNo state machine to draw.")
        return
    _, machine = machines[0]
    Path(path).write_text(f"{machine:mermaid}\n")
    print(f"\nGround-truth Mermaid diagram written to {path}")


def module_description(module_name: str) -> Any:
    module = importlib.import_module(f"thrs.control.modules.{module_name}.control")
    description = next(
        (
            getattr(module, attr)
            for attr in dir(module)
            if attr.endswith("_MODULE_DESCRIPTION")
        ),
        None,
    )
    if description is None:
        raise SystemExit(
            f"{module_name} has no *_MODULE_DESCRIPTION — it is a helper/sub-module, "
            "not a top-level control module. Document it inside its parent's manual."
        )
    return description


def build_control(description: Any) -> Any:
    return description.control(description.parameters_cls(), datetime.now)


def print_facts(description: Any, control: Any) -> None:
    describe_parameters(description.parameters_cls)
    describe_alarms(description.alarms())
    describe_io(description)
    describe_modes(description, control)
    describe_state_machines(control)


MODULES_PACKAGE = "thrs.control.modules"


def source_modules(description: Any, control: Any) -> list[ModuleType]:
    """Control-module files that define the module's behaviour, sub-controls included.

    The whole file is hashed rather than the callbacks the facts name: constants,
    the control loop and helper classes hold behaviour a manual describes too.
    """
    owners = [
        control,
        description.alarms(),
        description.parameters_cls,
        *(sub for _, sub in state_machines(control)),
    ]
    modules = {
        inspect.getmodule(owner if inspect.isclass(owner) else type(owner))
        for owner in owners
    }
    return sorted(
        (
            module
            for module in modules
            if module is not None and module.__name__.startswith(MODULES_PACKAGE)
        ),
        key=lambda module: module.__name__,
    )


def fingerprint(module_name: str) -> str:
    """Short hash of the module's facts and source, which a published manual is stamped with."""
    description = module_description(module_name)
    control = build_control(description)
    facts = io.StringIO()
    with contextlib.redirect_stdout(facts):
        print_facts(description, control)
    sources = "".join(
        Path(module.__file__).read_text()
        for module in source_modules(description, control)
        if module.__file__ is not None
    )
    return hashlib.sha256((facts.getvalue() + sources).encode()).hexdigest()[:7]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", help="module name, e.g. pcm, dhw, pvt, thrusters")
    parser.add_argument("--diagram", help="also write the raw Mermaid state diagram")
    args = parser.parse_args()

    description = module_description(args.module)
    control = build_control(description)
    print(f"# Facts for `{args.module}`\n")
    print_facts(description, control)

    if args.diagram:
        write_diagram(control, args.diagram)


if __name__ == "__main__":
    main()
