import logging
import re
from dataclasses import dataclass
from enum import StrEnum

from more_itertools import partition

from .types import IOTopic

logger = logging.getLogger(__name__)


class ComponentType(StrEnum):
    VALVE = "valve"
    PUMP = "pump"
    TEMPERATURE = "temperature"
    FLOW = "flow"
    PRESSURE = "pressure"
    RH33 = "rh33"
    PYRANOMETER = "pyranometer"
    LEVEL_SWITCH = "level_switch"
    LEVEL_SENSOR = "level_sensor"
    AMCS_MODE = "amcs_mode"
    CALCULATED_FLOW = "calculated_flow"
    CALCULATED_TEMPERATURE = "calculated_temperature"
    HEAT_TRANSFER = "heat_transfer"


SYSTEMS = (
    "250000-fresh-water",
    "250000-tech-water",
    "340000-sewage",
    "380000-sea-water",
    "500000-thrs",
)
COMPONENTS = {
    "mix": ComponentType.VALVE,
    "switch": ComponentType.VALVE,
    "flowcontrol": ComponentType.VALVE,
    "pump": ComponentType.PUMP,
    "pump1": ComponentType.PUMP,
    "pump2": ComponentType.PUMP,
    "temperature": ComponentType.TEMPERATURE,
    "flow": ComponentType.FLOW,
    "pressure": ComponentType.PRESSURE,
    "power": ComponentType.RH33,
    "pyranometer": ComponentType.PYRANOMETER,
    "level-switch": ComponentType.LEVEL_SWITCH,
    "level": ComponentType.LEVEL_SENSOR,
    "mode": ComponentType.AMCS_MODE,
}

# Sort component keys by length in descending order to match the longest key first
component_keys = sorted(COMPONENTS.keys(), key=len, reverse=True)
system_pattern = re.compile(r"\d{6}-([^/]+)")
component_pattern = re.compile(r"^.*?-(.*)")


@dataclass
class ManagedTopic:
    system_name: str
    module_name: str
    technical_name: str
    component: ComponentType
    topic: IOTopic


def extract_parts(topic: IOTopic) -> ManagedTopic | str:
    # example topics
    # marpower/500000-thrs/thrusters/thrusters-switch-aft
    # marpower/500000-thrs/dhw/dhw-temperature-dc-return
    # marpower/500000-thrs/pcm/pcm-flow-module3
    # marpower/250000-fresh-water/hot/hot-flow-crew-cabin-sb-mid
    parts = topic.topic.split("/", maxsplit=3)
    if len(parts) < 4:
        return "Not enough topic parts"
    if "/" in parts[3]:
        return "To many topic parts"
    match = system_pattern.match(parts[1])
    if not match:
        return "System part is not formatted correctly"

    system_name = match.group(1).replace("-", "_")
    module_name = parts[2]
    technical_name = parts[3]
    if technical_name == "mode":
        component_string = "mode"
        technical_name = f"{module_name}-mode"
    else:
        match = component_pattern.match(technical_name)
        if not match:
            return "Component is not formatted correctly"
        component_string = match.group(1)

    for component_key in component_keys:
        if component_string == component_key or component_string.startswith(
            component_key + "-"
        ):
            return ManagedTopic(
                system_name,
                module_name,
                technical_name,
                COMPONENTS[component_key],
                topic,
            )
    return "Component is not of known type"


def extract_managed_topics(
    topics: list[IOTopic],
) -> tuple[list[ManagedTopic], list[IOTopic], list[IOTopic]]:
    """Extract managed topics from the given list of topics."""

    other_topics, matched_topics = partition(
        lambda topic: topic.topic.startswith(
            tuple(f"marpower/{system}/" for system in SYSTEMS)
        ),
        topics,
    )
    parsed_topics = [(extract_parts(topic), topic) for topic in matched_topics]
    managed_topics = [
        parts for parts, _ in parsed_topics if isinstance(parts, ManagedTopic)
    ]
    invalid_topics = [
        (parts, topic)
        for parts, topic in parsed_topics
        if not isinstance(parts, ManagedTopic)
    ]

    for topic in invalid_topics:
        logger.warning(f"Invalid managed topic {topic[1].topic}: {topic[0]}")

    return (
        managed_topics,
        [topic for _, topic in invalid_topics],
        list(other_topics),
    )
