from typing import Annotated

from pydantic import ConfigDict
from pydantic.alias_generators import to_snake

from thrs.input_output.base import (
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class DrivesSensorValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    drives_pump1: Annotated[
        sensor.Pump, component_meta(yard_tag="50001028", component_type="pump")
    ]
    drives_pump2: Annotated[
        sensor.Pump, component_meta(yard_tag="50001029", component_type="pump")
    ]
    drives_temperature_shorepower_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-11", component_type="temperature_sensor"),
    ]
    drives_temperature_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-14", component_type="temperature_sensor"),
    ]
    drives_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-16", component_type="temperature_sensor"),
    ]
    drives_temperature_recovery_mix: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-57", component_type="temperature_sensor"),
    ]
    drives_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-59", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_aft1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-32", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_fwd1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-61", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrives_fwd_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-62", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrives_aft_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-63", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_aft2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-64", component_type="temperature_sensor"),
    ]
    drives_temperature_propdrive_fwd2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-72", component_type="temperature_sensor"),
    ]
    drives_mix_exchanger: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001046-01", component_type="valve", valve_type="mix"
        ),
    ]
    drives_mix_recovery: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001046-03", component_type="valve", valve_type="mix"
        ),
    ]
    drives_flow_shorepower: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-10", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_aft1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-13", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_fwd2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-14", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_fwd1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-15", component_type="flow_sensor"),
    ]
    drives_flow_propdrive_aft2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-16", component_type="flow_sensor"),
    ]
    drives_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-03", component_type="flow_sensor"),
    ]
    drives_flowcontrol_propdrive_aft: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001065-02", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_flowcontrol_propdrive_fwd: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001065-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_switch_shorepower_supply: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-04", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_shorepower_return: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-05", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_aft1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-06", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_aft2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-09", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_fwd1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-07", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_fwd2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-08", component_type="valve", valve_type="switch"
        ),
    ]
    drives_pressure: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-10", component_type="pressure_sensor"),
    ]
    drives_propdrive_aft1: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002079",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pms/esi_active",
        ),
    ]
    drives_propdrive_aft2: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002079",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pcs/aradex-aft2-active",
        ),
    ]
    drives_propdrive_fwd1: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002080",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pcs/aradex-fwd1-active",
        ),
    ]
    drives_propdrive_fwd2: Annotated[
        sensor.PropulsionDrive,
        component_meta(
            yard_tag="45002080",  # TODO: figure out correct yard tag. We do expect separate signal from each Aradex
            component_type="propulsion_drive",
            included_in_fmu=False,
            topic_override="dummy-pcs/aradex-fwd2-active",
        ),
    ]
    drives_shorepower: Annotated[
        sensor.ShorePowerConverter,
        component_meta(
            yard_tag="45002001",
            component_type="shore_power_converter",
            included_in_fmu=False,
            topic_override="dummy-pcs/shorepower-active",
        ),
    ]


class DrivesControlValues(ThrsValues):
    model_config = ConfigDict(
        alias_generator=to_snake,
        use_enum_values=True,
        validate_by_name=True,
    )

    drives_pump1: Annotated[
        control.Pump, component_meta(yard_tag="50001028", component_type="pump")
    ]
    drives_pump2: Annotated[
        control.Pump, component_meta(yard_tag="50001029", component_type="pump")
    ]
    drives_mix_exchanger: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001046-01", component_type="valve", valve_type="mix"
        ),
    ]
    drives_mix_recovery: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001046-03", component_type="valve", valve_type="mix"
        ),
    ]
    drives_flowcontrol_propdrive_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001065-02", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_flowcontrol_propdrive_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001065-03", component_type="valve", valve_type="flowcontrol"
        ),
    ]
    drives_switch_shorepower_supply: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-04", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_shorepower_return: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-05", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_aft1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-06", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_aft2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-09", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_fwd1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-07", component_type="valve", valve_type="switch"
        ),
    ]
    drives_switch_propdrive_fwd2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-08", component_type="valve", valve_type="switch"
        ),
    ]


class DrivesSimulationInputs(ThrsValues):
    drives_oil_cooler_aft: simulation.HeatSource
    drives_oil_cooler_fwd: simulation.HeatSource
    drives_propdrive_aft1: simulation.PropulsionDrive
    drives_propdrive_aft2: simulation.PropulsionDrive
    drives_propdrive_fwd1: simulation.PropulsionDrive
    drives_propdrive_fwd2: simulation.PropulsionDrive
    drives_shorepower: simulation.Converter
    drives_seawater_supply: simulation.Boundary
    drives_dhw_supply: simulation.Boundary


class DrivesSimulationOutputs(ThrsValues):
    drives_seawater_return: simulation.TemperatureBoundary
    drives_dhw_exchanger: simulation.ExchangerBoundary
    drives_dhw_return: simulation.TemperatureBoundary
