from unittest.mock import Mock

import pytest

from thrs.orchestration.comms import ControlChannels, SimulationChannels
from thrs.orchestration.config import Config
from thrs.runtime.descriptions.simulation import lookup_mode


def subscribed_topics(settings: Config, subscribe_device_values: bool) -> set[str]:
    mode = lookup_mode("thrusters")
    assert mode.simulation_description is not None
    connector = Mock()

    for module_name, description in mode.control_modules.items():
        ControlChannels(
            connector,
            settings,
            module_name,
            description,
            subscribe_device_values=subscribe_device_values,
        )
    SimulationChannels(
        connector,
        settings,
        {name: desc.sensor_values_cls for name, desc in mode.control_modules.items()},
        {name: desc.control_values_cls for name, desc in mode.control_modules.items()},
        type(mode.simulation_description.simulation_inputs),
        mode.simulation_description.simulation_outputs_cls,
        subscribe_device_values=subscribe_device_values,
    )

    return {
        topic
        for registration in connector._register_listener.call_args_list
        for topic in registration.args[0].subscribe_topics()
    }


@pytest.mark.parametrize(
    ("subscribe_device_values", "expect_device_topics"),
    [(True, True), (False, False)],
)
def test_device_value_subscriptions_follow_the_flag(
    settings: Config, subscribe_device_values: bool, expect_device_topics: bool
):
    topics = subscribed_topics(settings, subscribe_device_values)

    device_topics = {
        topic
        for topic in topics
        if topic.startswith(f"{settings.mqtt_devices_topic_prefix}/")
    }
    assert bool(device_topics) == expect_device_topics


def test_commands_stay_subscribed_without_device_values(settings: Config):
    topics = subscribed_topics(settings, subscribe_device_values=False)

    assert f"{settings.mqtt_controller_topic_prefix}/thrusters/parameters/set" in topics
    assert f"{settings.mqtt_simulator_topic_prefix}/simulation-inputs/set" in topics
