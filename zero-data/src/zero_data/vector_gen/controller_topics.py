# TODO: generate this from asyncapi spec
from zero_data.io_list.managed_topics import ManagedTopic
from zero_data.io_list.types import IOTopic

THRS_CALCULATED_DEVICES = {
    "calculated_flows": {
        "dhw": ("dhw_freshwater_flow_supply",),
        "pvt": (
            "pvt_flow_main_aft_strings",
            "pvt_flow_main_fwd_strings",
            "pvt_flow_owners_strings",
            "pvt_total_flow",
            "pvt_seawater_exchanger_flow",
        ),
        "thrusters": ("thrusters_flow",),
    },
    "calculated_temperatures": {
        "pcm": ("pcm_temperature_consumers_return",),
        "pvt": (
            "pvt_max_temperature_main_aft_strings",
            "pvt_max_temperature_main_fwd_strings",
            "pvt_max_temperature_owners_strings",
            "pvt_temperature_main_aft_strings_supply",
            "pvt_temperature_main_fwd_strings_supply",
            "pvt_temperature_owners_strings_supply",
            "pvt_temperature_main_aft_strings_return",
            "pvt_temperature_main_fwd_strings_return",
            "pvt_temperature_owners_strings_return",
            "pvt_return_temperature",
        ),
        "thrusters": (
            "thrusters_temperature_recovery",
            "thrusters_temperature_pre_cooler",
        ),
    },
    "heat_transfers": {
        "adsorption": (
            "adsorption_ht_exchanger",
            "adsorption_dhw_exchanger",
        ),
        "consumers": (
            "consumers_adsorption_exchanger",
            "consumers_dhw_exchanger",
        ),
        "dc": ("dc_dhw_exchanger",),
        "dhw": (
            "dhw_hvac_exchanger",
            "dhw_heatpump_heat",
            "dhw_adsorption_exchanger",
            "dhw_consumers_exchanger",
            "dhw_dc_exchanger",
            "dhw_drives_exchanger",
        ),
        "drives": ("drives_dhw_exchanger",),
        "pcm": (
            "pcm_heat_module1",
            "pcm_heat_module1_freshwater",
            "pcm_heat_module2",
            "pcm_heat_module3",
            "pcm_heat_module4",
        ),
        "pvt": (
            "pvt_pvt_main_fwd_heat",
            "pvt_pvt_main_aft_heat",
            "pvt_pvt_owners_heat",
            "pvt_seawater_exchanger",
        ),
        "thrusters": (
            "thrusters_thruster_aft_heat",
            "thrusters_thruster_fwd_heat",
            "thrusters_seawater_exchanger",
        ),
    },
}


def generate_controller_managed_topics():
    return [
        ManagedTopic(
            component,
            technical_name,
            "thrs",
            IOTopic(
                f"thrs/controller/{module}/{technical_name.replace('_', '-')}", [], ""
            ),
        )
        for component, data in THRS_CALCULATED_DEVICES.items()
        for module, technical_names in data.items()
        for technical_name in technical_names
    ]
