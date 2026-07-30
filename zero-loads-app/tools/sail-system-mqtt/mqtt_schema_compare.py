import argparse
import asyncio
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aiomqtt import Client

from loads.config import settings


def _json_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return "unknown"


def _flatten_payload(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    flattened: dict[str, str] = {}
    for key, value in data.items():
        joined = f"{prefix}/{key}" if prefix else key
        if isinstance(value, dict):
            flattened.update(_flatten_payload(value, joined))
        else:
            flattened[joined] = _json_type(value)
    return flattened


def _expand_refs(node: Any, defs: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            return _expand_refs(defs.get(ref.split("/")[-1], {}), defs)
        return {key: _expand_refs(value, defs) for key, value in node.items()}
    if isinstance(node, list):
        return [_expand_refs(item, defs) for item in node]
    return node


def _flatten_schema_properties(
    schema_obj: dict[str, Any], prefix: str = ""
) -> dict[str, str]:
    flattened: dict[str, str] = {}
    properties = schema_obj.get("properties", {})

    if not isinstance(properties, dict):
        return flattened

    for key, value in properties.items():
        joined = f"{prefix}/{key}" if prefix else key
        if not isinstance(value, dict):
            continue
        if value.get("type") == "object" and isinstance(value.get("properties"), dict):
            flattened.update(_flatten_schema_properties(value, joined))
        else:
            flattened[joined] = value.get("type", "unknown")
    return flattened


def _load_topics_from_file(path: Path) -> list[str]:
    topics: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value.startswith("sail-systems/"):
            topics.append(value)
    return topics


def _select_topics(
    args: argparse.Namespace, schema_topics: dict[str, Any]
) -> list[str]:
    if args.topics:
        return sorted(set(args.topics))
    if args.topics_file:
        return sorted(set(_load_topics_from_file(Path(args.topics_file))))
    if args.all_topics:
        return sorted(schema_topics.keys())
    return sorted(schema_topics.keys())


async def _collect_payloads(
    topics: list[str], samples_per_topic: int, timeout_seconds: int
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, int],
    dict[str, int],
    dict[str, list[str]],
]:
    collected: dict[str, list[dict[str, Any]]] = {topic: [] for topic in topics}
    invalid_json_count: dict[str, int] = {topic: 0 for topic in topics}
    total_messages_seen: dict[str, int] = {topic: 0 for topic in topics}
    raw_samples: dict[str, list[str]] = {topic: [] for topic in topics}

    async with Client(
        settings.mqtt_host,
        settings.mqtt_port,
        username=settings.mqtt_username,
        password=settings.mqtt_password,
    ) as client:
        for topic in topics:
            await client.subscribe(topic, qos=1)

        done_event = asyncio.Event()

        async def _consume_messages() -> None:
            async for message in client.messages:
                topic = message.topic.value
                if topic not in collected:
                    continue

                total_messages_seen[topic] += 1
                payload_text = (
                    message.payload.decode("utf-8", errors="replace")
                    if isinstance(message.payload, (bytes, bytearray))
                    else str(message.payload)
                )

                try:
                    decoded = json.loads(payload_text)
                    if isinstance(decoded, dict):
                        collected[topic].append(decoded)
                    else:
                        invalid_json_count[topic] += 1
                        raw_samples[topic].append(payload_text[:1000])
                except json.JSONDecodeError:
                    invalid_json_count[topic] += 1
                    raw_samples[topic].append(payload_text[:1000])

                done = all(
                    len(samples) >= samples_per_topic for samples in collected.values()
                )
                if done:
                    done_event.set()
                    return

        consumer_task = asyncio.create_task(_consume_messages())

        try:
            await asyncio.wait_for(done_event.wait(), timeout=timeout_seconds)
        except TimeoutError:
            pass
        finally:
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

    return collected, invalid_json_count, total_messages_seen, raw_samples


def _build_observed_schema(
    collected: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    topics_schema: dict[str, Any] = {}

    for topic, samples in collected.items():
        key_types: dict[str, set[str]] = defaultdict(set)
        key_counts: dict[str, int] = defaultdict(int)

        for sample in samples:
            flat = _flatten_payload(sample)
            for key, value_type in flat.items():
                key_types[key].add(value_type)
                key_counts[key] += 1

        properties: dict[str, Any] = {}
        for key in sorted(key_types.keys()):
            observed_types = sorted(key_types[key])
            properties[key] = {
                "types": observed_types,
                "present_in_samples": key_counts[key],
            }

        topics_schema[topic] = {
            "sample_count": len(samples),
            "properties": properties,
        }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "broker": {
            "host": settings.mqtt_host,
            "port": settings.mqtt_port,
        },
        "topics": topics_schema,
    }


def _build_diff_report(
    expected_schema: dict[str, Any],
    observed_schema: dict[str, Any],
    invalid_json_count: dict[str, int],
    total_messages_seen: dict[str, int],
    selected_topics: list[str],
    report_scope: str,
) -> dict[str, Any]:
    def _types_compatible(expected_type: str, observed_types: list[str]) -> bool:
        # JSON Schema treats integer as a subset of number.
        if expected_type == "number":
            return any(
                observed_type in {"number", "integer"}
                for observed_type in observed_types
            )
        return expected_type in observed_types

    defs = expected_schema.get("$defs", {})
    expected_topics = expected_schema.get("topics", {})
    observed_topics = observed_schema.get("topics", {})

    expected_topic_set = set(expected_topics.keys())
    observed_topic_set = set(observed_topics.keys())
    selected_topic_set = set(selected_topics)

    if report_scope == "all":
        report_topic_set = expected_topic_set | observed_topic_set
    elif report_scope == "observed":
        report_topic_set = observed_topic_set
    else:
        # selected: show only topics the user requested for this run.
        report_topic_set = selected_topic_set

    topic_reports: dict[str, Any] = {}

    for topic in sorted(report_topic_set):
        expected_raw = expected_topics.get(topic)
        observed_raw = observed_topics.get(topic)

        expected_flat: dict[str, str] = {}
        observed_flat: dict[str, list[str]] = {}

        if isinstance(expected_raw, dict):
            expanded = _expand_refs(expected_raw, defs)
            expected_flat = _flatten_schema_properties(expanded)

        if isinstance(observed_raw, dict):
            observed_props = observed_raw.get("properties", {})
            if isinstance(observed_props, dict):
                observed_flat = {
                    key: value.get("types", [])
                    for key, value in observed_props.items()
                    if isinstance(value, dict)
                }

        expected_keys = set(expected_flat.keys())
        observed_keys = set(observed_flat.keys())

        missing_keys = sorted(expected_keys - observed_keys)
        unexpected_keys = sorted(observed_keys - expected_keys)

        type_mismatches: list[dict[str, Any]] = []
        for key in sorted(expected_keys & observed_keys):
            expected_type = expected_flat.get(key)
            observed_types = observed_flat.get(key, [])
            if (
                expected_type
                and observed_types
                and not _types_compatible(expected_type, observed_types)
            ):
                type_mismatches.append(
                    {
                        "key": key,
                        "expected_type": expected_type,
                        "observed_types": observed_types,
                    }
                )

        topic_reports[topic] = {
            "status": (
                "missing_in_expected"
                if topic not in expected_topic_set
                else "missing_in_observed"
                if topic not in observed_topic_set
                else "compared"
            ),
            "messages_seen": total_messages_seen.get(topic, 0),
            "invalid_json_count": invalid_json_count.get(topic, 0),
            "expected_key_count": len(expected_keys),
            "observed_key_count": len(observed_keys),
            "missing_keys": missing_keys,
            "unexpected_keys": unexpected_keys,
            "type_mismatches": type_mismatches,
        }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "report_scope": report_scope,
            "selected_topic_count": len(selected_topic_set),
            "expected_topic_count": len(expected_topic_set),
            "observed_topic_count": len(observed_topic_set),
            "missing_topics": sorted(
                topic
                for topic in report_topic_set
                if topic in expected_topic_set and topic not in observed_topic_set
            ),
            "unexpected_topics": sorted(
                topic
                for topic in report_topic_set
                if topic in observed_topic_set and topic not in expected_topic_set
            ),
        },
        "topics": topic_reports,
    }


def _build_text_summary(diff_report: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = diff_report.get("summary", {})

    lines.append("MQTT Schema Comparison Summary")
    lines.append("================================")
    lines.append(f"Report scope: {summary.get('report_scope', 'selected')}")
    lines.append(f"Selected topics: {summary.get('selected_topic_count', 0)}")
    lines.append(
        f"Expected topics (schema total): {summary.get('expected_topic_count', 0)}"
    )
    lines.append(
        f"Observed topics (capture total): {summary.get('observed_topic_count', 0)}"
    )
    lines.append("")

    missing_topics = summary.get("missing_topics", [])
    unexpected_topics = summary.get("unexpected_topics", [])

    lines.append(f"Missing topics: {len(missing_topics)}")
    lines.append(f"Unexpected topics: {len(unexpected_topics)}")
    lines.append("")

    for topic, report in sorted(diff_report.get("topics", {}).items()):
        if report.get("status") != "compared":
            continue

        missing_keys = report.get("missing_keys", [])
        unexpected_keys = report.get("unexpected_keys", [])
        type_mismatches = report.get("type_mismatches", [])

        if not missing_keys and not unexpected_keys and not type_mismatches:
            continue

        lines.append(f"Topic: {topic}")
        lines.append(f"  Messages seen: {report.get('messages_seen', 0)}")
        lines.append(f"  Missing keys: {len(missing_keys)}")
        lines.append(f"  Unexpected keys: {len(unexpected_keys)}")
        lines.append(f"  Type mismatches: {len(type_mismatches)}")

        if missing_keys:
            lines.append("  Missing keys:")
            lines.extend([f"    - {key}" for key in missing_keys])
        if unexpected_keys:
            lines.append("  Unexpected keys:")
            lines.extend([f"    - {key}" for key in unexpected_keys])
        if type_mismatches:
            lines.append("  Type mismatches:")
            lines.extend(
                [
                    "    - "
                    f"{entry['key']}: expected={entry['expected_type']} "
                    f"observed={entry['observed_types']}"
                    for entry in type_mismatches
                ]
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _parse_args() -> argparse.Namespace:
    base_dir = Path(__file__).resolve().parent
    default_schema = base_dir / "sail-system-mqtt-schema.json"
    default_topics_file = base_dir / "sail-system-topics.txt"
    default_output_prefix = base_dir / "sail-system-mqtt-live"

    parser = argparse.ArgumentParser(
        description="Capture live MQTT payload schema and compare it with expected schema."
    )
    parser.add_argument(
        "--expected-schema",
        default=str(default_schema),
        help="Path to expected schema JSON (default: sail-system-mqtt-schema.json).",
    )
    parser.add_argument(
        "--topics-file",
        default=str(default_topics_file),
        help="Path to topics file (default: sail-system-topics.txt).",
    )
    parser.add_argument(
        "--topics",
        nargs="*",
        help="Explicit topic list. If provided, topics-file and all-topics are ignored.",
    )
    parser.add_argument(
        "--all-topics",
        action="store_true",
        help="Use all topics from expected schema topics map.",
    )
    parser.add_argument(
        "--samples-per-topic",
        type=int,
        default=1,
        help="How many valid JSON messages to capture per topic (default: 1).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=60,
        help="Global capture timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--output-prefix",
        default=str(default_output_prefix),
        help="Output prefix. Writes <prefix>.observed.json, <prefix>.diff.json, <prefix>.summary.txt.",
    )
    parser.add_argument(
        "--report-scope",
        choices=["selected", "observed", "all"],
        default="selected",
        help=(
            "Topic scope for diff/summary: selected (requested topics only), "
            "observed (only topics with captured samples), all (full expected vs observed universe)."
        ),
    )
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> None:
    expected_schema_path = Path(args.expected_schema)
    expected_schema = json.loads(expected_schema_path.read_text(encoding="utf-8"))
    expected_topics = expected_schema.get("topics", {})

    topics = _select_topics(args, expected_topics)
    if not topics:
        raise ValueError(
            "No topics selected. Provide --topics, --topics-file, or --all-topics."
        )

    (
        collected,
        invalid_json_count,
        total_messages_seen,
        raw_samples,
    ) = await _collect_payloads(
        topics=topics,
        samples_per_topic=args.samples_per_topic,
        timeout_seconds=args.timeout_seconds,
    )

    observed_schema = _build_observed_schema(collected)
    observed_schema["capture"] = {
        "samples_per_topic_target": args.samples_per_topic,
        "timeout_seconds": args.timeout_seconds,
        "topic_count": len(topics),
        "invalid_json_count": invalid_json_count,
        "messages_seen": total_messages_seen,
        "invalid_json_samples": raw_samples,
    }

    diff_report = _build_diff_report(
        expected_schema=expected_schema,
        observed_schema=observed_schema,
        invalid_json_count=invalid_json_count,
        total_messages_seen=total_messages_seen,
        selected_topics=topics,
        report_scope=args.report_scope,
    )

    summary_text = _build_text_summary(diff_report)

    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    observed_path = output_prefix.with_suffix(".observed.json")
    diff_path = output_prefix.with_suffix(".diff.json")
    summary_path = output_prefix.with_suffix(".summary.txt")

    observed_path.write_text(json.dumps(observed_schema, indent=2), encoding="utf-8")
    diff_path.write_text(json.dumps(diff_report, indent=2), encoding="utf-8")
    summary_path.write_text(summary_text, encoding="utf-8")

    print(f"Wrote observed schema: {observed_path}")
    print(f"Wrote diff report: {diff_path}")
    print(f"Wrote summary: {summary_path}")


def main() -> None:
    args = _parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
