from dataclasses import dataclass
from typing import TypeGuard

from more_itertools import partition

from .types import IOTopic
import re

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

def extract_parts(topic: IOTopic) -> tuple[str, str] | None:
    # example topics
    # marpower/500000-thrs/thrusters/thrusters-switch-aft
    # marpower/500000-thrs/dhw/dhw-temperature-dc-return
    # marpower/500000-thrs/pcm/pcm-flow-module3
    parts = topic.topic.split("/")
    if len(parts) < 4:
        return None
    technical_name = parts[3]

    # Sort table keys by length in descending order to match the longest key first
    table_keys = sorted(TABLES.keys(), key=len, reverse=True)

    match = re.compile(r'^.*?-(.*)').match(technical_name)
    if not match:
        return None
    component_string = match.group(1)
    for table_key in table_keys:
        if component_string == table_key or component_string.startswith(table_key + '-'):
            return TABLES[table_key], technical_name
    return None


@dataclass
class ThrsTopic:
    component: str
    technical_name: str
    topic: IOTopic


def _has_extracted_parts(
    topic_with_parts: tuple[tuple[str, str] | None, IOTopic],
) -> TypeGuard[tuple[tuple[str, str], IOTopic]]:
    return topic_with_parts[0] is not None


def extract_thrs_topics(
    topics: list[IOTopic],
) -> tuple[list[ThrsTopic], list[IOTopic], list[IOTopic]]:
    """Extract topics that are relevant for THRS from the given list of topics."""

    other_topics, thrs_topics = partition(
        lambda topic: topic.topic.startswith("marpower/500000-thrs"),
        topics,
    )
    parsed_thrs_topics = [(extract_parts(topic), topic) for topic in thrs_topics]
    valid_thrs_topics = [
        topic_with_parts
        for topic_with_parts in parsed_thrs_topics
        if _has_extracted_parts(topic_with_parts)
    ]
    invalid_thrs_topics = [
        topic for parts, topic in parsed_thrs_topics if parts is None
    ]
    valids_wrapped = [
        ThrsTopic(component, technical_name, topic)
        for (component, technical_name), topic in valid_thrs_topics
    ]

    return (
        valids_wrapped,
        invalid_thrs_topics,
        list(other_topics),
    )
