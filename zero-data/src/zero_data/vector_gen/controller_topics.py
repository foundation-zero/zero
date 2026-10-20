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
        "drives": (
            # "drives-flow-propdrive-aft",
            # "drives-flow-propdrive-fwd",
            # "drives-total-flow",
        ),
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
        "adsorption": ("adsorption-temperature-waste-supply-before-seawater",),
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
            "adsorption-hot-heat",
            "adsorption-waste-heat",
            "adsorption-cooling-heat",
            "adsorption-ht-exchanger",
            "adsorption-dhw-exchanger",
            "adsorption-seawater-exchanger",
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
        "drives": (
            "drives-propdrive-aft1-heat",
            "drives-propdrive-aft2-heat",
            "drives-aft-oil-cooler-heat",
            "drives-propdrive-fwd1-heat",
            "drives-propdrive-fwd2-heat",
            "drives-fwd-oil-cooler-heat",
            "drives-shorepower-heat",
            "drives-dhw-exchanger",
            "drives-seawater-exchanger",
        ),
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
    "pid_controllers": {
        "adsorption": (
            "adsorption-hot-mix-controller",
            "adsorption-recovery-controller",
            "adsorption-waste-cooling-controller",
        ),
        "consumers": (
            "consumers-dhw-flow-controller",
            "consumers-bypass-flow-controller",
            "consumers-adsorption-flow-controller",
        ),
        "dc": (
            "dc-heat-dump-controller",
            "dc-recovery-mix-controller",
            "dc-brightloops-aft-pump-controller",
            "dc-brightloops-aft-warmup-mix-controller",
            "dc-brightloops-fwd-pump-controller",
            "dc-brightloops-fwd-warmup-mix-controller",
            "dc-ugrids-pump-controller",
            "dc-ugrids-warmup-mix-controller",
        ),
        "dhw": (
            "dhw-pump-flow-controller",
            "dhw-drives-flow-controller",
            "dhw-dc-flow-controller",
        ),
        "drives": (
            "drives-heat-dump-controller",
            "drives-recovery-mix-controller",
            "drives-pump-controller-shorepower",
            "drives-pump-controller-propulsion",
            "drives-aft-flow-controller",
            "drives-fwd-flow-controller",
        ),
        "pcm": (
            "pcm-pump-flow-controller",
            "pcm-module1-flow-controller",
            "pcm-module2-flow-controller",
            "pcm-module3-flow-controller",
            "pcm-module4-flow-controller",
        ),
        "pvt": (
            "pvt-heat-dump-controller",
            "pvt-main-aft-warmup-mix-controller",
            "pvt-main-aft-pump-controller",
            "pvt-main-fwd-warmup-mix-controller",
            "pvt-main-fwd-pump-controller",
            "pvt-owners-warmup-mix-controller",
            "pvt-owners-pump-controller",
        ),
        "thrusters": (
            "thrusters-heat-dump-controller",
            "thrusters-warmup-mix-controller",
            "thrusters-pump-controller",
            "thrusters-aft-recovery-temperature-controller",
            "thrusters-fwd-recovery-temperature-controller",
            "thrusters-aft-flow-controller",
            "thrusters-fwd-flow-controller",
        ),
    },
    "tank_controllers": {
        "dhw": ("dhw-tanks-controller",),
    },
    "pcm_charge_controllers": {
        "pcm": (
            "pcm-module1-charge-controller",
            "pcm-module2-charge-controller",
            "pcm-module3-charge-controller",
            "pcm-module4-charge-controller",
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
