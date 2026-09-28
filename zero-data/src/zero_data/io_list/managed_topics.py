import re
from dataclasses import dataclass
from typing import TypeGuard

from more_itertools import partition

from .types import IOTopic

SYSTEMS = (
    "250000-fresh-water",
    "250000-tech-water",
    "340000-sewage",
    "380000-sea-water",
    "500000-thrs",
)
TABLES = {
    "mix": "valves",
    "switch": "valves",
    "flowcontrol": "valves",
    "pump": "pumps",
    "pump1": "pumps",
    "pump2": "pumps",
    "temperature": "temperatures",
    "flow": "flows",
    "pressure": "pressures",
    "power": "rh33s",
    "pyranometer": "pyranometers",
    "level-switch": "level_switches",
    "level": "level_sensors",
}

# Sort table keys by length in descending order to match the longest key first
table_keys = sorted(TABLES.keys(), key=len, reverse=True)
system_pattern = re.compile(r"\d{6}-([^/]+)")
component_pattern = re.compile(r"^.*?-(.*)")


def extract_parts(topic: IOTopic) -> tuple[str, str, str] | None:
    # example topics
    # marpower/500000-thrs/thrusters/thrusters-switch-aft
    # marpower/500000-thrs/dhw/dhw-temperature-dc-return
    # marpower/500000-thrs/pcm/pcm-flow-module3
    # marpower/250000-fresh-water/hot/hot-flow-crew-cabin-sb-mid
    parts = topic.topic.split("/")
    if len(parts) < 4:
        return None
    match = system_pattern.match(parts[1])
    if not match:
        return None
    system_name = match.group(1).replace("-", "_")
    technical_name = parts[3]
    match = component_pattern.match(technical_name)
    if not match:
        return None
    component_string = match.group(1)
    for table_key in table_keys:
        if component_string == table_key or component_string.startswith(
            table_key + "-"
        ):
            return TABLES[table_key], technical_name, system_name
    return None


@dataclass
class ManagedTopic:
    component: str
    technical_name: str
    system_name: str
    topic: IOTopic


def _has_extracted_parts(
    topic_with_parts: tuple[tuple[str, str, str] | None, IOTopic],
) -> TypeGuard[tuple[tuple[str, str, str], IOTopic]]:
    return topic_with_parts[0] is not None


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
    valid_topics = [
        topic_with_parts
        for topic_with_parts in parsed_topics
        if _has_extracted_parts(topic_with_parts)
    ]
    invalid_topics = [topic for parts, topic in parsed_topics if parts is None]
    managed_topics = [
        ManagedTopic(component, technical_name, system_name, topic)
        for (component, technical_name, system_name), topic in valid_topics
    ]

    return (
        managed_topics,
        invalid_topics,
        list(other_topics),
    )
