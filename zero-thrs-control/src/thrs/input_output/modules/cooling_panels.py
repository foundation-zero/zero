from typing import Annotated

from thrs.input_output.base import (
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor


class CoolingPanelsSensorValues(ThrsValues):
    cooling_pump_hydronic: Annotated[
        sensor.Pump, component_meta(yard_tag="50001037", component_type="pump")
    ]
    cooling_temperature_adsorption_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-42", component_type="temperature_sensor"),
    ]
    cooling_temperature_adsorption_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-43", component_type="temperature_sensor"),
    ]
    cooling_temperature_hydronic_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-67", component_type="temperature_sensor"),
    ]
    cooling_temperature_hydronic_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-68", component_type="temperature_sensor"),
    ]
    cooling_temperature_main_deckhouse: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="41006032-1", component_type="temperature_sensor"),
    ]
    cooling_temperature_ps_aft: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="41006032-2", component_type="temperature_sensor"),
    ]
    cooling_temperature_sb_aft: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="41006032-3", component_type="temperature_sensor"),
    ]
    cooling_temperature_ps_fwd: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="41006032-4", component_type="temperature_sensor"),
    ]
    cooling_temperature_sb_fwd: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="41006032-5", component_type="temperature_sensor"),
    ]
    cooling_flow_hydronic: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-01", component_type="flow_sensor"),
    ]
    cooling_power_owners_deckhouse: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-1", component_type="power_sensor"),
    ]
    cooling_power_owners_ps: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-2", component_type="power_sensor"),
    ]
    cooling_power_french: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-3", component_type="power_sensor"),
    ]
    cooling_power_italian: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-4", component_type="power_sensor"),
    ]
    cooling_power_owners_sb: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-5", component_type="power_sensor"),
    ]
    cooling_power_dutch: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-6", component_type="power_sensor"),
    ]
    cooling_power_california: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-7", component_type="power_sensor"),
    ]
    cooling_power_main_deckhouse: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-8", component_type="power_sensor"),
    ]
    cooling_power_polynesian: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-11", component_type="power_sensor"),
    ]
    cooling_power_mission_room: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-12", component_type="power_sensor"),
    ]
    cooling_power_laundry: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-13", component_type="power_sensor"),
    ]
    cooling_power_crew_mess: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-15", component_type="power_sensor"),
    ]
    cooling_power_crew5: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-16", component_type="power_sensor"),
    ]
    cooling_power_crew3: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-17", component_type="power_sensor"),
    ]
    cooling_power_crew1: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-18", component_type="power_sensor"),
    ]
    cooling_power_crew6: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-19", component_type="power_sensor"),
    ]
    cooling_power_crew4: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-20", component_type="power_sensor"),
    ]
    cooling_power_crew2: Annotated[
        sensor.PowerSensor,
        component_meta(yard_tag="41006052-21", component_type="power_sensor"),
    ]
    cooling_mix_main_deckhouse: Annotated[
        sensor.Valve,
        component_meta(yard_tag="41006031", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_ps_aft: Annotated[
        sensor.Valve,
        component_meta(yard_tag="41006029-1", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_ps_fwd: Annotated[
        sensor.Valve,
        component_meta(yard_tag="41006029-3", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_sb_aft: Annotated[
        sensor.Valve,
        component_meta(yard_tag="41006029-2", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_sb_fwd: Annotated[
        sensor.Valve,
        component_meta(yard_tag="41006029-4", component_type="valve", valve_type="mix"),
    ]
    cooling_switch_california: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-7", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-18", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-21", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew3: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-17", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew4: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-20", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew5: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-16", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew6: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-19", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew_mess: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-15", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_dutch: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-6", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_french: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-3", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_italian: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-4", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_laundry: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-13")
    ]
    cooling_switch_main_deckhouse: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-8", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_mission_room: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-12", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_owners_deckhouse: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-1", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_owners_ps: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-2", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_owners_sb: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-5", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_polynesian: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="41006011-11", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_pump_main_deckhouse: Annotated[
        sensor.Pump, component_meta(yard_tag="41006001-1", component_type="pump")
    ]
    cooling_pump_ps_aft: Annotated[
        sensor.Pump, component_meta(yard_tag="41006001-2", component_type="pump")
    ]
    cooling_pump_ps_fwd: Annotated[
        sensor.Pump, component_meta(yard_tag="41006001-4", component_type="pump")
    ]
    cooling_pump_sb_aft: Annotated[
        sensor.Pump, component_meta(yard_tag="41006001-3", component_type="pump")
    ]
    cooling_pump_sb_fwd: Annotated[
        sensor.Pump, component_meta(yard_tag="41006001-5", component_type="pump")
    ]


class CoolingPanelsControlValues(ThrsValues):
    cooling_pump_hydronic: Annotated[
        control.Pump, component_meta(yard_tag="50001037", component_type="pump")
    ]
    cooling_mix_main_deckhouse: Annotated[
        control.Valve,
        component_meta(yard_tag="41006031", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_ps_aft: Annotated[
        control.Valve,
        component_meta(yard_tag="41006029-1", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_ps_fwd: Annotated[
        control.Valve,
        component_meta(yard_tag="41006029-3", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_sb_aft: Annotated[
        control.Valve,
        component_meta(yard_tag="41006029-2", component_type="valve", valve_type="mix"),
    ]
    cooling_mix_sb_fwd: Annotated[
        control.Valve,
        component_meta(yard_tag="41006029-4", component_type="valve", valve_type="mix"),
    ]
    cooling_switch_california: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-7", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-18", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-21", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew3: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-17", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew4: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-20", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew5: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-16", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew6: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-19", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_crew_mess: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-15", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_dutch: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-6", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_french: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-3", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_italian: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-4", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_laundry: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-13", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_main_deckhouse: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-8", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_mission_room: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-12", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_owners_deckhouse: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-1", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_owners_ps: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-2", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_owners_sb: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-5", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_switch_polynesian: Annotated[
        control.Valve,
        component_meta(
            yard_tag="41006011-11", component_type="valve", valve_type="switch"
        ),
    ]
    cooling_pump_main_deckhouse: Annotated[
        control.Pump, component_meta(yard_tag="41006001-1", component_type="pump")
    ]
    cooling_pump_ps_aft: Annotated[
        control.Pump, component_meta(yard_tag="41006001-2", component_type="pump")
    ]
    cooling_pump_ps_fwd: Annotated[
        control.Pump, component_meta(yard_tag="41006001-4", component_type="pump")
    ]
    cooling_pump_sb_aft: Annotated[
        control.Pump, component_meta(yard_tag="41006001-3", componenentt_type="pump")
    ]
    cooling_pump_sb_fwd: Annotated[
        control.Pump, component_meta(yard_tag="41006001-5", component_type="pump")
    ]


class CoolingPanelsSimulationInputs(ThrsValues):
    pass


class CoolingPanelsSimulationOutputs(ThrsValues):
    pass
