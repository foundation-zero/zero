# TODO: generate this from asyncapi spec
from zero_data.io_list.managed_topics import ManagedTopic
from zero_data.io_list.types import IOTopic

THRS_CALCULATED_DEVICES: dict[str, dict[str, tuple[str, ...]]] = {
    "calculated_flows": {
        "dc": (
            "dc-total-flow",
            "dc-aft-flow",
            "dc-ugrid-flow",
            "dc-fwd-flow",
        ),
        "dhw": ("dhw-freshwater-flow-supply",),
        "pvt": (
            "pvt-flow-main-aft-strings",
            "pvt-flow-main-fwd-strings",
            "pvt-flow-owners-strings",
            "pvt-total-flow",
            "pvt-seawater-exchanger-flow",
        ),
        "thrusters": ("thrusters-flow",),
    },
    "calculated_temperatures": {
        "pcm": ("pcm-temperature-consumers-return",),
        "pvt": (
            "pvt-max-temperature-main-aft-strings",
            "pvt-max-temperature-main-fwd-strings",
            "pvt-max-temperature-owners-strings",
            "pvt-temperature-main-aft-strings-supply",
            "pvt-temperature-main-fwd-strings-supply",
            "pvt-temperature-owners-strings-supply",
            "pvt-temperature-main-aft-strings-return",
            "pvt-temperature-main-fwd-strings-return",
            "pvt-temperature-owners-strings-return",
            "pvt-return-temperature",
        ),
        "thrusters": (
            "thrusters-temperature-recovery",
            "thrusters-temperature-pre-cooler",
        ),
    },
    "heat_transfers": {
        "adsorption": (
            "adsorption-ht-exchanger",
            "adsorption-dhw-exchanger",
        ),
        "consumers": (
            "consumers-adsorption-exchanger",
            "consumers-dhw-exchanger",
        ),
        "dc": (
            "dc-dhw-exchanger",
            "dc-seawater-exchanger",
            "dc-aft-heat",
            "dc-ugrid-heat",
            "dc-fwd-heat",
        ),
        "dhw": (
            "dhw-hvac-exchanger",
            "dhw-heatpump-heat",
            "dhw-adsorption-exchanger",
            "dhw-consumers-exchanger",
            "dhw-dc-exchanger",
            "dhw-drives-exchanger",
        ),
        "drives": ("drives-dhw-exchanger",),
        "pcm": (
            "pcm-heat-module1",
            "pcm-heat-module1-freshwater",
            "pcm-heat-module2",
            "pcm-heat-module3",
            "pcm-heat-module4",
            "pcm-freshwater-heat",
        ),
        "pvt": (
            "pvt-pvt-main-fwd-heat",
            "pvt-pvt-main-aft-heat",
            "pvt-pvt-owners-heat",
            "pvt-seawater-exchanger",
            "pvt-pcm-heat",
        ),
        "thrusters": (
            "thrusters-thruster-aft-heat",
            "thrusters-thruster-fwd-heat",
            "thrusters-seawater-exchanger",
            "thrusters-pcm-heat",
        ),
    },
}


def generate_controller_managed_topics():
    return [
        ManagedTopic(
            component,
            technical_name,
            "thrs",
            IOTopic(f"thrs/controller/{module}/{technical_name}", [], ""),
        )
        for component, data in THRS_CALCULATED_DEVICES.items()
        for module, technical_names in data.items()
        for technical_name in technical_names
    ]
