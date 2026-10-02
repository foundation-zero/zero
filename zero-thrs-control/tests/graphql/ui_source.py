"""The GraphQL documents zero-ui's thrsim module sends, read from its source.

The UI is the consumer the migration must not break, so the suites that
speak for it do not retype its documents: they read them from the UI's own
source - the query literals (``stores/*.ts``), the fragment modules
(``lib/queries.generated.ts`` and ``lib/consts.ts``), the mutation
templates (``stores/thrs.ts``, ``stores/simulation.ts``,
``graphql/index.ts``) and which input types its forms send with which fields
(``components/controls/*.vue``). A pattern that no longer matches fails
loudly, so a UI change cannot silently drop coverage.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

UI_DIR = Path(__file__).resolve().parents[3] / "zero-ui" / "src" / "modules" / "thrsim"


def ui_source(relative: str) -> str:
    path = UI_DIR / relative
    if not path.exists():
        pytest.skip(f"zero-ui source not found at {path}")
    return path.read_text(encoding="utf-8")


def ui_match(pattern: str, src: str) -> str:
    match = re.search(pattern, src, re.DOTALL)
    assert match is not None, f"zero-ui source no longer matches {pattern!r}"
    return match.group(1)


def fragments() -> dict[str, str]:
    """``queries.generated.ts``: fragment name -> selection text."""
    generated = ui_source("lib/queries.generated.ts")
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r"export const (\w+) = `(.*?)`;", generated, re.DOTALL)
    }


def query_map(name: str) -> list[tuple[str, str]]:
    """A ``consts.ts`` map of keys to ``Queries.X`` fragments, in order."""
    consts = ui_source("lib/consts.ts")
    body = ui_match(rf"export const {name}[^=]*=\s*\{{(.*?)\}};", consts)
    return re.findall(r"(\w+):\s*Queries\.(\w+)", body)


def module_queries() -> dict[str, dict[str, str]]:
    """``QUERIES``: module -> section -> selection text."""
    consts = ui_source("lib/consts.ts")
    body = ui_match(r"export const QUERIES = toQueries\(\{(.*?)\n\}\);", consts)
    frags = fragments()
    return {
        module: {
            section: frags[fragment]
            for section, fragment in re.findall(r"(\w+):\s*Queries\.(\w+)", sections)
        }
        for module, sections in re.findall(r"(\w+):\s*\{(.*?)\}", body, re.DOTALL)
    }


def simulation_input_queries() -> dict[str, str]:
    """``SIMULATION_INPUT_QUERIES``: simulation -> selection text."""
    frags = fragments()
    return {
        key: frags[fragment] for key, fragment in query_map("SIMULATION_INPUT_QUERIES")
    }


def control_query() -> str:
    return ui_match(
        r"gql`\s*(query ControlStatus.*?)`", ui_source("stores/automation.ts")
    )


def status_query() -> str:
    return ui_match(
        r"gql`\s*(query SimulationStatus.*?)`", ui_source("stores/simulation.ts")
    )


def query_all() -> str:
    """Rebuild ``QUERY_ALL`` the way consts.ts does: substitute each
    ``${Queries.X}`` with the generated fragment, and expand
    ``${toUnionQueries(SIMULATION_*_QUERIES, toInputType/toOutputType)}`` into
    the ``... on <Key>Simulation<Inputs|Outputs>Type { __typename <fragment> }``
    members for every key of the map."""
    consts = ui_source("lib/consts.ts")
    frags = fragments()
    template = ui_match(r"gql`\s*(query QueryAll.*?)`;", consts)

    def _union(map_name: str, suffix: str) -> str:
        return "\n".join(
            f"... on {key[0].upper()}{key[1:]}Simulation{suffix}Type {{ __typename {frags[frag]} }}"
            for key, frag in query_map(map_name)
        )

    template = template.replace(
        "${toUnionQueries(SIMULATION_INPUT_QUERIES, toInputType)}",
        _union("SIMULATION_INPUT_QUERIES", "Inputs"),
    ).replace(
        "${toUnionQueries(SIMULATION_OUTPUT_QUERIES, toOutputType)}",
        _union("SIMULATION_OUTPUT_QUERIES", "Outputs"),
    )
    return re.sub(r"\$\{Queries\.(\w+)\}", lambda m: frags[m.group(1)], template)


# --- Mutation documents --------------------------------------------------------


def form_mutation(input_type: str, mutation: str, return_values_query: str) -> str:
    """A form submit (``controlValuesForm`` in stores/thrs.ts): its template
    with the input type, mutation name and return selection filled in."""
    template = ui_match(
        r"const query = `(mutation \(\$input: \$\{inputType\}\) \{.*?)`;",
        ui_source("stores/thrs.ts"),
    )
    return (
        template.replace("${inputType}", input_type)
        .replace("${mutation}", mutation)
        .replace("${returnValuesQuery}", return_values_query)
    )


def advisory_mutation(mutation: str, return_values_query: str) -> str:
    """The advisory switch (``setAdvisory`` in stores/simulation.ts)."""
    template = ui_match(
        r"const query = `(mutation \(\$input: AmcsControlModeInputType!\) \{.*?)`;",
        ui_source("stores/simulation.ts"),
    )
    return template.replace("${mutation}", mutation).replace(
        "${SIMULATION_INPUT_QUERIES[type]}", return_values_query
    )


def mutation_with_value(mutation: str, input_name: str, value_type: str) -> str:
    """``mutationWithValue`` (graphql/index.ts)."""
    template = ui_match(
        r"mutationWithValue = \([^)]*\) =>\s*gql`\s*(mutation MutationWithValue.*?)`",
        ui_source("graphql/index.ts"),
    )
    return (
        template.replace("${valueType}", value_type)
        .replace("${mutationName}", mutation)
        .replace("${inputName}", input_name)
    )


def mutation_without_value(mutation: str) -> str:
    """``mutationWithoutValue`` (graphql/index.ts)."""
    template = ui_match(
        r"mutationWithoutValue = \([^)]*\) =>\s*gql`\s*(mutation MutationWithoutValue.*?)`",
        ui_source("graphql/index.ts"),
    )
    return template.replace("${mutationName}", mutation)


def directive_calls() -> dict[str, tuple[str, str] | None]:
    """The simulation directives stores/simulation.ts sends: name ->
    (argument name, value type), or None for one without a value."""
    src = ui_source("stores/simulation.ts")
    calls: dict[str, tuple[str, str] | None] = {
        m.group(1): None for m in re.finditer(r'mutationWithoutValue\("(\w+)"\)', src)
    }
    for m in re.finditer(r'mutationWithValue\("(\w+)", "(\w+)", "([^"]+)"\)', src):
        calls[m.group(1)] = (m.group(2), m.group(3))
    assert calls, "stores/simulation.ts sends no directives any more?"
    return calls


def automation_call() -> tuple[str, str]:
    """(argument name, value type) of ``{module}SetAutomationMode``
    (stores/automation.ts)."""
    src = ui_source("stores/automation.ts")
    return (
        ui_match(r'mutationWithValue\(`\$\{module\}SetAutomationMode`, "(\w+)"', src),
        ui_match(
            r'mutationWithValue\(`\$\{module\}SetAutomationMode`, "\w+", "([^"]+)"\)',
            src,
        ),
    )


def form_inputs() -> dict[str, list[str]]:
    """Every input type a form sends (``controlValuesForm`` calls in
    components/controls/*.vue) with the fields it sends. A scalar parameter
    form sends the bare value (fields ``["value"]``)."""
    forms: dict[str, list[str]] = {}
    for vue in sorted((UI_DIR / "components" / "controls").glob("*.vue")):
        src = vue.read_text(encoding="utf-8")
        for m in re.finditer(
            r'controlValuesForm\(\s*props\.\w+,\s*MutationType\.\w+,\s*"([^"]+)",'
            r"\s*props\.componentName,\s*\w+,\s*\[([^\]]*)\]",
            src,
        ):
            forms[m.group(1)] = re.findall(r'"(\w+)"', m.group(2))
    assert forms, "no controlValuesForm calls found in components/controls"
    return forms
