from typing import Annotated
from thrs.input_output.base import SimulationInputs, ThrsModel, component_meta
from thrs.input_output.definitions import control, sensor


class CoolingPanelsSensorValues(ThrsModel):
    cooling_pump_hydronic: Annotated[sensor.Pump, component_meta(yard_tag="50001037")]
    cooling_temperature_hydronic_return: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-67")
    ]
    cooling_temperature_hydronic_supply: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="50001038-68")
    ]
    cooling_temperature_main_deckhouse: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="41006032-1")
    ]
    cooling_temperature_ps_aft: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="41006032-2")
    ]
    cooling_temperature_sb_aft: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="41006032-3")
    ]
    cooling_temperature_ps_fwd: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="41006032-4")
    ]
    cooling_temperature_sb_fwd: Annotated[
        sensor.TemperatureSensor, component_meta(yard_tag="41006032-5")
    ]
    cooling_flow_hydronic: Annotated[
        sensor.FlowSensor, component_meta(yard_tag="50001058-01")
    ]
    cooling_power_owners_deckhouse: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-1")
    ]
    cooling_power_owners_ps: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-2")
    ]
    cooling_power_french: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-3")
    ]
    cooling_power_italian: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-4")
    ]
    cooling_power_owners_sb: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-5")
    ]
    cooling_power_dutch: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-6")
    ]
    cooling_power_california: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-7")
    ]
    cooling_power_main_deckhouse: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-8")
    ]
    cooling_power_polynesian: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-11")
    ]
    cooling_power_mission_room: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-12")
    ]
    cooling_power_laundry: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-13")
    ]
    cooling_power_crew_mess: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-15")
    ]
    cooling_power_crew_5: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-16")
    ]
    cooling_power_crew_3: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-17")
    ]
    cooling_power_crew_1: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-18")
    ]
    cooling_power_crew_6: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-19")
    ]
    cooling_power_crew_4: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-20")
    ]
    cooling_power_crew_2: Annotated[
        sensor.PowerSensor, component_meta(yard_tag="41006058-21")
    ]
    cooling_mix_main_deckhouse: Annotated[
        sensor.Valve, component_meta(yard_tag="41006031-1")
    ]
    cooling_mix_ps_aft: Annotated[sensor.Valve, component_meta(yard_tag="41006029-1")]
    cooling_mix_ps_fwd: Annotated[sensor.Valve, component_meta(yard_tag="41006029-3")]
    cooling_mix_sb_aft: Annotated[sensor.Valve, component_meta(yard_tag="41006029-2")]
    cooling_mix_sb_fwd: Annotated[sensor.Valve, component_meta(yard_tag="41006029-4")]
    cooling_switch_california: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-7")
    ]
    cooling_switch_crew_1: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-18")
    ]
    cooling_switch_crew_2: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-21")
    ]
    cooling_switch_crew_3: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-17")
    ]
    cooling_switch_crew_4: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-20")
    ]
    cooling_switch_crew_5: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-16")
    ]
    cooling_switch_crew_6: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-19")
    ]
    cooling_switch_crew_mess: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-15")
    ]
    cooling_switch_dutch: Annotated[sensor.Valve, component_meta(yard_tag="41006011-6")]
    cooling_switch_french: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-3")
    ]
    cooling_switch_italian: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-4")
    ]
    cooling_switch_laundry: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-13")
    ]
    cooling_switch_main_deckhouse: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-8")
    ]
    cooling_switch_mission_room: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-12")
    ]
    cooling_switch_owners_deckhouse: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-1")
    ]
    cooling_switch_owners_ps: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-2")
    ]
    cooling_switch_owners_sb: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-5")
    ]
    cooling_switch_polynesian: Annotated[
        sensor.Valve, component_meta(yard_tag="41006011-11")
    ]
    cooling_pump_main_deckhouse: Annotated[
        sensor.Pump, component_meta(yard_tag="41006001-1")
    ]
    cooling_pump_ps_aft: Annotated[sensor.Pump, component_meta(yard_tag="41006001-2")]
    cooling_pump_ps_fwd: Annotated[sensor.Pump, component_meta(yard_tag="41006001-4")]
    cooling_pump_sb_aft: Annotated[sensor.Pump, component_meta(yard_tag="41006001-3")]
    cooling_pump_sb_fwd: Annotated[sensor.Pump, component_meta(yard_tag="41006001-5")]


class CoolingPanelsControlValues(ThrsModel):
    cooling_pump_hydronic: Annotated[control.Pump, component_meta(yard_tag="50001037")]
    cooling_mix_main_deckhouse: Annotated[
        control.Valve, component_meta(yard_tag="41006031-1")
    ]
    cooling_mix_ps_aft: Annotated[control.Valve, component_meta(yard_tag="41006029-1")]
    cooling_mix_ps_fwd: Annotated[control.Valve, component_meta(yard_tag="41006029-3")]
    cooling_mix_sb_aft: Annotated[control.Valve, component_meta(yard_tag="41006029-2")]
    cooling_mix_sb_fwd: Annotated[control.Valve, component_meta(yard_tag="41006029-4")]
    cooling_switch_california: Annotated[
        control.Valve, component_meta(yard_tag="41006011-7")
    ]
    cooling_switch_crew_1: Annotated[
        control.Valve, component_meta(yard_tag="41006011-18")
    ]
    cooling_switch_crew_2: Annotated[
        control.Valve, component_meta(yard_tag="41006011-21")
    ]
    cooling_switch_crew_3: Annotated[
        control.Valve, component_meta(yard_tag="41006011-17")
    ]
    cooling_switch_crew_4: Annotated[
        control.Valve, component_meta(yard_tag="41006011-20")
    ]
    cooling_switch_crew_5: Annotated[
        control.Valve, component_meta(yard_tag="41006011-16")
    ]
    cooling_switch_crew_6: Annotated[
        control.Valve, component_meta(yard_tag="41006011-19")
    ]
    cooling_switch_crew_mess: Annotated[
        control.Valve, component_meta(yard_tag="41006011-15")
    ]
    cooling_switch_dutch: Annotated[
        control.Valve, component_meta(yard_tag="41006011-6")
    ]
    cooling_switch_french: Annotated[
        control.Valve, component_meta(yard_tag="41006011-3")
    ]
    cooling_switch_italian: Annotated[
        control.Valve, component_meta(yard_tag="41006011-4")
    ]
    cooling_switch_laundry: Annotated[
        control.Valve, component_meta(yard_tag="41006011-13")
    ]
    cooling_switch_main_deckhouse: Annotated[
        control.Valve, component_meta(yard_tag="41006011-8")
    ]
    cooling_switch_mission_room: Annotated[
        control.Valve, component_meta(yard_tag="41006011-12")
    ]
    cooling_switch_owners_deckhouse: Annotated[
        control.Valve, component_meta(yard_tag="41006011-1")
    ]
    cooling_switch_owners_ps: Annotated[
        control.Valve, component_meta(yard_tag="41006011-2")
    ]
    cooling_switch_owners_sb: Annotated[
        control.Valve, component_meta(yard_tag="41006011-5")
    ]
    cooling_switch_polynesian: Annotated[
        control.Valve, component_meta(yard_tag="41006011-11")
    ]
    cooling_pump_main_deckhouse: Annotated[
        control.Pump, component_meta(yard_tag="41006001-1")
    ]
    cooling_pump_ps_aft: Annotated[control.Pump, component_meta(yard_tag="41006001-2")]
    cooling_pump_ps_fwd: Annotated[control.Pump, component_meta(yard_tag="41006001-4")]
    cooling_pump_sb_aft: Annotated[control.Pump, component_meta(yard_tag="41006001-3")]
    cooling_pump_sb_fwd: Annotated[control.Pump, component_meta(yard_tag="41006001-5")]


class CoolingPanelsSimulationInputs(SimulationInputs):
    pass


class CoolingPanelsSimulationOutputs(ThrsModel):
    pass
