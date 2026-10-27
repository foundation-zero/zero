import re
from dataclasses import dataclass

GROUP_DEFINITION = re.compile(
    r'export const (\w+_GROUP) = group\(\s*"([^"]+)",\s*PositionId\.\w+,(.*?)\);',
    re.DOTALL,
)
OVERVIEW_DEFINITION = re.compile(
    r"export const OVERVIEW = dashboard\((.*?)\);", re.DOTALL
)
VARIABLE_ID = re.compile(r'"([a-z0-9-]+)"')
GROUP_CONSTANT = re.compile(r"\w+_GROUP")


@dataclass(frozen=True)
class OverviewGroup:
    name: str
    technical_names: tuple[str, ...]


def read_overview_groups(dashboards_ts: str) -> tuple[OverviewGroup, ...]:
    """Parse the groups of OVERVIEW from zero-ui/src/modules/loads/lib/consts.dashboards.ts."""
    group_definitions = {
        constant: OverviewGroup(name, tuple(VARIABLE_ID.findall(variables)))
        for constant, name, variables in GROUP_DEFINITION.findall(dashboards_ts)
    }
    overview = OVERVIEW_DEFINITION.search(dashboards_ts)
    if overview is None:
        raise ValueError("OVERVIEW dashboard not found in the UI dashboards")

    overview_constants = GROUP_CONSTANT.findall(overview.group(1))
    unparsed_constants = [
        constant for constant in overview_constants if constant not in group_definitions
    ]
    if unparsed_constants:
        raise ValueError(f"Overview groups not parsed: {unparsed_constants}")

    overview_groups = tuple(
        group_definitions[constant] for constant in overview_constants
    )
    empty_groups = [
        group.name for group in overview_groups if not group.technical_names
    ]
    if empty_groups:
        raise ValueError(f"Overview groups without variables: {empty_groups}")
    return overview_groups
