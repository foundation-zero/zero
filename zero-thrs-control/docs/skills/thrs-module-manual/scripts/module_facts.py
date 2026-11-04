"""Dump the documentable facts of a thrs control module.

Everything here is read from the live objects rather than from the source text,
so the output cannot drift from the code the way a hand-read summary can. Run it
from `zero-thrs-control` with `uv run python <this file> <module>`.

    uv run python docs/skills/thrs-module-manual/scripts/module_facts.py pcm
    uv run python ... pcm --diagram /tmp/pcm_truth.png

`--diagram` writes the raw pytransitions/graphviz rendering of the state machine.
That picture is the ground truth to check a redrawn figure against; it is too
dense to ship in a manual.
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

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.input_output.definitions.units import UnitMeta

# Display units for the `modelica_name` carried by each unit alias in
# thrs.input_output.definitions.units.
UNITS: dict[str, str] = {
    "C": "°C",
    "K": "K",
    "l_min": "l/min",
    "ratio": "0–1",
    "Bar": "bar",
    "Watt": "W",
    "s": "s",
    "Joule": "J",
    "Liter": "L",
    "Hz": "Hz",
    "Degree": "°",
    "bool": "on/off",
}

# Bounds that belong to the unit itself (a Celsius cannot go below absolute
# zero) rather than to the parameter. Reporting them would bury the handful of
# bounds that actually constrain an engineer.
INTRINSIC_BOUNDS: set[tuple[str, str, float]] = {
    ("C", "ge", -273.15),
    ("Hz", "ge", -0.1),
    ("Bar", "ge", -1.0),
    ("Liter", "ge", 0.0),
    ("Degree", "ge", 0.0),
    ("Degree", "le", 360.0),
}


def unit_of(metadata: list[Any]) -> str | None:
    meta = next((m for m in metadata if isinstance(m, UnitMeta)), None)
    return meta.modelica_name if meta else None


def bounds_of(metadata: list[Any], unit: str | None) -> list[str]:
    out: list[str] = []
    for m in metadata:
        for attr, symbol in (("ge", "≥"), ("gt", ">"), ("le", "≤"), ("lt", "<")):
            value = getattr(m, attr, None)
            if value is None:
                continue
            if (unit, attr, float(value)) in INTRINSIC_BOUNDS:
                continue
            out.append(f"{symbol} {value}")
    return out


def source_of(fn: Any) -> str:
    """Readable name for a state hook or transition condition.

    Conditions are often lambdas closing over parameters; their name is
    `<lambda>`, so fall back to the source line, which is what actually tells
    you when the transition fires.
    """
    if isinstance(fn, str):
        return fn
    name = getattr(fn, "__name__", None)
    if name and name != "<lambda>":
        return name
    try:
        text = " ".join(inspect.getsource(fn).split())
    except OSError, TypeError:
        return str(fn)
    if "lambda" in text:
        return text[text.index("lambda") :].rstrip(",").rstrip()
    return text


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def describe_parameters(parameters_cls: type) -> None:
    print("## Parameters\n")
    print("Each line: name | unit | default | bounds | description in the code")
    for name, field in parameters_cls.model_fields.items():
        unit = unit_of(list(field.metadata))
        display = UNITS.get(unit or "", unit or "")
        default = field.default
        if isinstance(default, tuple) and len(default) == 3:
            display = display or "PID (Kp, Ki, Kd)"
        bounds = ", ".join(bounds_of(list(field.metadata), unit)) or "-"
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
    for name in description.control_mode_cls.model_fields:
        print(f"- {name}")
    print()
    for label, member in (
        ("mode", type(control).mode),
        ("initial_mode", type(control).initial_mode),
        ("modes()", getattr(type(control), "modes", None)),
    ):
        target = getattr(member, "fget", member)
        if target is None:
            continue
        try:
            print(f"### `{label}`\n")
            print(inspect.getsource(target).rstrip())
            print()
        except OSError, TypeError:
            continue


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
        try:
            sub = getattr(control, attr)
        except Exception:
            continue
        if sub is not control and getattr(sub, "_states", None):
            subs.append((f"sub-control `{attr}`", sub))
    top = [("top level", control)] if getattr(control, "_states", None) else []
    return top + list({id(sub): (label, sub) for label, sub in subs}.values())


def describe_state_machines(control: Any) -> None:
    print("## State machine(s)\n")
    machines = state_machines(control)
    for label, obj in machines:
        print(f"### {label} — {type(obj).__name__}\n")
        for state in obj._states:
            print(f"- state `{state.name}`")
            for hook in ("on_enter", "on_exit"):
                names = [source_of(h) for h in as_list(getattr(state, hook, None))]
                if names:
                    print(f"    - {hook}: {', '.join(names)}")
        print()
        for transition in getattr(obj, "_transitions", None) or []:
            conditions = [source_of(c) for c in as_list(transition.get("conditions"))]
            unless = [source_of(c) for c in as_list(transition.get("unless"))]
            line = (
                f"- `{transition['source']}` --[{transition['trigger']}]--> "
                f"`{transition['dest']}`"
            )
            if conditions:
                line += f"\n    - when ALL of: {'; '.join(conditions)}"
            if unless:
                line += f"\n    - unless ANY of: {'; '.join(unless)}"
            print(line)
        print()

    if not machines:
        print(
            "(no state machine — this module is continuous control only, so the "
            "manual needs a different figure, or none)\n"
        )


def draw_diagram(control: Any, states: Any, transitions: Any, path: str) -> None:
    from transitions.extensions import GraphMachine

    GraphMachine(
        model=control,
        states=states,
        transitions=transitions,
        graph_engine="pygraphviz",
        initial=getattr(control, "state", None) or states[0].name,
        show_conditions=True,
        show_state_attributes=True,
    )
    control.get_graph().draw(path, prog="dot")
    print(f"\nGround-truth diagram written to {path}")


def find_machine(control: Any) -> tuple[Any, Any, Any] | None:
    machines = state_machines(control)
    if not machines:
        return None
    _, machine = machines[0]
    return machine, machine._states, machine._transitions


def module_description(module_name: str) -> Any:
    module = importlib.import_module(f"thrs.control.modules.{module_name}")
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
    return description.control(
        description.parameters_cls(), datetime.now, MachineStateLoggingServiceNoop()
    )


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
    parser.add_argument("--diagram", help="also write the raw graphviz state diagram")
    args = parser.parse_args()

    description = module_description(args.module)
    control = build_control(description)
    print(f"# Facts for `{args.module}`\n")
    print_facts(description, control)

    if args.diagram:
        machine = find_machine(control)
        if machine is None:
            print("\nNo state machine to draw.")
        else:
            draw_diagram(*machine, args.diagram)


if __name__ == "__main__":
    main()
