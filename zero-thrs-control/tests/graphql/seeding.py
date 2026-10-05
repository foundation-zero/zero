"""One complete, deterministic THRS state on MQTT, for the suites that read
it back through both APIs.

Every module's device topics (sensor readings merged with the actuated
``CC_*`` control keys, as a device publishes them), its controller objects
(manual values, parameters, controller state, control mode), the computed
sensor fields the control loop would publish, and one simulation's status,
inputs and outputs - retained, under both services' prefixes
(``stack_config``). The control loop must not be ticking, or its publishes
overwrite the seed.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

from aiomqtt import Client as MqttClient

from tests.graphql.parity import seed_distinct_values
from tests.graphql.stack_config import (
    MQTT_HOST,
    MQTT_PORT,
    mqtt_graphql_config,
    thrs_api_config,
)
from thrs.control.switching import SwitchingControlMode
from thrs.input_output.base import ThrsValues
from thrs.input_output.definitions.wire_context import AMCS_RECEIVE_CONTEXT
from thrs.orchestration.comms import PartialMqttMapping, device_module_prefix
from thrs.runtime.descriptions.simulation import simulation_io_classes
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec.asyncapi import all_module_descriptions

_CONFIGS = (thrs_api_config(), mqtt_graphql_config())
DEVICES_PREFIXES = tuple(dict.fromkeys(c.mqtt_devices_topic_prefix for c in _CONFIGS))
CONTROLLER_PREFIXES = tuple(
    dict.fromkeys(c.mqtt_controller_topic_prefix for c in _CONFIGS)
)
SIMULATOR_PREFIXES = tuple(
    dict.fromkeys(c.mqtt_simulator_topic_prefix for c in _CONFIGS)
)

# The simulation whose inputs/outputs are seeded (thrs-api resolves the union
# member by which model validates; the UI selects `... on <X>SimulationInputsType`).
SEEDED_SIMULATION = "thrusters"
SEEDED_SIMULATION_TIME = datetime(2026, 1, 2, 3, 4, 5, 678901, tzinfo=UTC)

# Seconds both subscribers get to cache the retained seed before a query.
SETTLE_S = 3.0


def seeded(cls: type[ThrsValues]) -> ThrsValues:
    """A zero model with distinct values on every float leaf."""
    model = cls.zero()
    seed_distinct_values(model)
    return model


def control_mode_instance(cls: type[ThrsValues]) -> ThrsValues:
    """A populated control-mode model: every ``str`` field gets a marker
    value, nested groups recurse, a fieldless model is just empty."""
    values: dict[str, Any] = {}
    for name, fld in cls.model_fields.items():
        base = fld.annotation
        if isinstance(base, type) and issubclass(base, ThrsValues):
            values[name] = control_mode_instance(base)
        else:
            values[name] = f"seeded-{name}"
    return cls(**values)


async def seed_all(mqtt: MqttClient) -> None:
    modules = all_module_descriptions()
    # A device publishes one payload per component carrying both its sensor
    # readings and the actuated (`CC_*`) control keys; the APIs read
    # sensorValues and controlValues off the same topics. Merge the two
    # serializations per topic so both sections complete. A topic two modules
    # share carries the module seeded last.
    device_payloads: dict[str, dict[str, Any]] = {}
    sensor_mappings: dict[str, PartialMqttMapping[Any]] = {}
    for module, desc in modules.items():
        sensors = seeded(desc.sensor_values_cls)
        actuated = seeded(desc.control_values_cls)
        module_prefix = device_module_prefix(module)
        for prefix in DEVICES_PREFIXES:
            sensor_mapping = PartialMqttMapping(type(sensors), prefix, module_prefix)
            sensor_mappings.setdefault(module, sensor_mapping)
            for topic, payload in sensor_mapping.split_to_topics(sensors).items():
                device_payloads.setdefault(topic, {}).update(json.loads(payload))
            actuated_mapping = PartialMqttMapping(
                type(actuated), prefix, module_prefix, context=AMCS_RECEIVE_CONTEXT
            )
            for topic, payload in actuated_mapping.split_to_topics(actuated).items():
                device_payloads.setdefault(topic, {}).update(json.loads(payload))
        objects = {
            "manual-values": seeded(desc.control_values_cls),
            "parameters": desc.parameters_cls(),
            "controller-state": seeded(desc.controller_state_cls),
            "control-mode": SwitchingControlMode[desc.control_mode_cls](
                automatic_mode=control_mode_instance(desc.control_mode_cls)
            ),
        }
        for kind, model in objects.items():
            payload = model.model_dump_json(by_alias=True)
            for prefix in CONTROLLER_PREFIXES:
                await mqtt.publish(
                    f"{prefix}/{module}/{kind}", payload=payload, retain=True
                )
    for topic, payload in device_payloads.items():
        await mqtt.publish(topic, payload=json.dumps(payload), retain=True)

    # The computed sensor fields, as the control loop publishes them for the
    # sensor values it receives from these device topics.
    for module, mapping in sensor_mappings.items():
        for topic, payload in device_payloads.items():
            mapping.handle_message(topic, json.dumps(payload))
        sensors = mapping.result()
        assert sensors is not None, f"{module}: seeded sensor values incomplete"
        for prefix in CONTROLLER_PREFIXES:
            computed_mapping = PartialMqttMapping.only_computed_fields(
                type(sensors), prefix, module
            )
            for topic, payload in computed_mapping.split_to_topics(sensors).items():
                await mqtt.publish(topic, payload=payload, retain=True)

    inputs_cls, outputs_cls = simulation_io_classes()[SEEDED_SIMULATION]
    status = SimulationStatusMessage(
        mode=SEEDED_SIMULATION,
        status="available",
        control_modules=[SEEDED_SIMULATION],
        simulation_time=SEEDED_SIMULATION_TIME,
    )
    seeded_io = {
        "status": status,
        "simulation-inputs": seeded(inputs_cls),
        "simulation-outputs": seeded(outputs_cls),
    }
    for kind, model in seeded_io.items():
        payload = model.model_dump_json(by_alias=True)
        for prefix in SIMULATOR_PREFIXES:
            await mqtt.publish(f"{prefix}/{kind}", payload=payload, retain=True)


def seed_state() -> None:
    """Seed the complete state once and give both subscribers time to cache it."""

    async def _run() -> None:
        async with MqttClient(MQTT_HOST, MQTT_PORT) as mqtt:
            await seed_all(mqtt)
            await asyncio.sleep(SETTLE_S)

    asyncio.run(_run())
