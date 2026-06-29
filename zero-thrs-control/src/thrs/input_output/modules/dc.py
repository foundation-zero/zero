from typing import Annotated

from thrs.input_output.base import (
    SimulationInputs,
    SimulationValues,
    ThrsValues,
    component_meta,
)
from thrs.input_output.definitions import control, sensor, simulation


class DcSensorValues(ThrsValues):
    dc_pump_aft: Annotated[
        sensor.Pump, component_meta(yard_tag="50001020", component_type="pump")
    ]
    dc_pump_ugrid: Annotated[
        sensor.Pump, component_meta(yard_tag="50001023", component_type="pump")
    ]
    dc_pump_fwd: Annotated[
        sensor.Pump, component_meta(yard_tag="50001025", component_type="pump")
    ]
    dc_temperature_aft4_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-05", component_type="temperature_sensor"),
    ]
    dc_temperature_aft3_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-06", component_type="temperature_sensor"),
    ]
    dc_temperature_aft2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-07", component_type="temperature_sensor"),
    ]
    dc_temperature_aft1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-08", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-09", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-10", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd2_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-12", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd1_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-13", component_type="temperature_sensor"),
    ]
    dc_temperature_aft_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-15", component_type="temperature_sensor"),
    ]
    dc_temperature_recovery_mix: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-17", component_type="temperature_sensor"),
    ]
    dc_temperature_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-18", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-19", component_type="temperature_sensor"),
    ]
    dc_temperature_aft_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-20", component_type="temperature_sensor"),
    ]
    dc_temperature_recovery: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-52", component_type="temperature_sensor"),
    ]
    dc_temperature_recovery_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-58", component_type="temperature_sensor"),
    ]
    dc_temperature_fwd_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-69", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid_supply: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-70", component_type="temperature_sensor"),
    ]
    dc_temperature_ugrid_return: Annotated[
        sensor.TemperatureSensor,
        component_meta(yard_tag="50001038-71", component_type="temperature_sensor"),
    ]
    dc_mix_fwd: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001042-03", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_aft: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001043-02", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_ugrid: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001045-01", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_recovery: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001046-04", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_exchanger: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001046-05", component_type="valve", valve_type="mix"
        ),
    ]
    dc_flow_aft4: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-04", component_type="flow_sensor"),
    ]
    dc_flow_aft3: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-05", component_type="flow_sensor"),
    ]
    dc_flow_aft2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-06", component_type="flow_sensor"),
    ]
    dc_flow_aft1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-07", component_type="flow_sensor"),
    ]
    dc_flow_ugrid2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-08", component_type="flow_sensor"),
    ]
    dc_flow_ugrid1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-09", component_type="flow_sensor"),
    ]
    dc_flow_fwd2: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-11", component_type="flow_sensor"),
    ]
    dc_flow_fwd1: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-12", component_type="flow_sensor"),
    ]
    dc_flow_aft_return: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-25", component_type="flow_sensor"),
    ]
    dc_flow_fwd_return: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001057-26", component_type="flow_sensor"),
    ]
    dc_flow_recovery: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-04", component_type="flow_sensor"),
    ]
    dc_flow_ugrid_return: Annotated[
        sensor.FlowSensor,
        component_meta(yard_tag="50001058-06", component_type="flow_sensor"),
    ]
    dc_switch_aft4: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001068-01", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_aft3: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001068-02", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_aft2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001068-03", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_aft1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001068-04", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_fwd2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001068-05", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_fwd1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001068-06", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_ugrid2: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-02", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_ugrid1: Annotated[
        sensor.Valve,
        component_meta(
            yard_tag="50001069-03", component_type="valve", valve_type="switch"
        ),
    ]
    dc_pressure_aft: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-07", component_type="pressure_sensor"),
    ]
    dc_pressure_ugrid: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-08", component_type="pressure_sensor"),
    ]
    dc_pressure_fwd: Annotated[
        sensor.PressureSensor,
        component_meta(yard_tag="50001097-09", component_type="pressure_sensor"),
    ]
    dc_brightloop_aft1: Annotated[
        sensor.Brightloop,
        component_meta(
            yard_tag="45002076",
            component_type="brightloop",
            included_in_fmu=False,
            topic_override="dummy-pms/brightloop-aft1-active",
        ),
    ]
    dc_brightloop_aft2: Annotated[
        sensor.Brightloop,
        component_meta(
            yard_tag="45002075",
            component_type="brightloop",
            included_in_fmu=False,
            topic_override="dummy-pms/brightloop-aft2-active",
        ),
    ]
    dc_brightloop_aft3: Annotated[
        sensor.Brightloop,
        component_meta(
            yard_tag="45002074",
            component_type="brightloop",
            included_in_fmu=False,
            topic_override="dummy-pms/brightloop-aft3-active",
        ),
    ]
    dc_brightloop_aft4: Annotated[
        sensor.Brightloop,
        component_meta(
            yard_tag="45002073",
            component_type="brightloop",
            included_in_fmu=False,
            topic_override="dummy-pms/brightloop-aft4-active",
        ),
    ]
    dc_brightloop_fwd1: Annotated[
        sensor.Brightloop,
        component_meta(
            yard_tag="45002078",
            component_type="brightloop",
            included_in_fmu=False,
            topic_override="dummy-pms/brightloop-fwd1-active",
        ),
    ]
    dc_brightloop_fwd2: Annotated[
        sensor.Brightloop,
        component_meta(
            yard_tag="45002077",
            component_type="brightloop",
            included_in_fmu=False,
            topic_override="dummy-pms/brightloop-fwd2-active",
        ),
    ]
    dc_ugrid1: Annotated[
        sensor.Ugrid,
        component_meta(
            yard_tag="45002082",
            component_type="ugrid",
            included_in_fmu=False,
            topic_override="dummy-pms/ugrid1-active",
        ),
    ]
    dc_ugrid2: Annotated[
        sensor.Ugrid,
        component_meta(
            yard_tag="45002081",
            component_type="ugrid",
            included_in_fmu=False,
            topic_override="dummy-pms/ugrid2-active",
        ),
    ]


class DcControlValues(ThrsValues):
    dc_pump_aft: Annotated[
        control.Pump, component_meta(yard_tag="50001020", component_type="pump")
    ]
    dc_pump_fwd: Annotated[
        control.Pump, component_meta(yard_tag="50001025", component_type="pump")
    ]
    dc_pump_ugrid: Annotated[
        control.Pump, component_meta(yard_tag="50001023", component_type="pump")
    ]
    dc_mix_aft: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001043-02", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_fwd: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001042-03", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_ugrid: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001045-01", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_recovery: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001046-04", component_type="valve", valve_type="mix"
        ),
    ]
    dc_mix_exchanger: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001046-05", component_type="valve", valve_type="mix"
        ),
    ]
    dc_switch_aft4: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001068-01", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_aft3: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001068-02", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_aft2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001068-03", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_aft1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001068-04", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_fwd2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001068-05", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_fwd1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001068-06", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_ugrid2: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-02", component_type="valve", valve_type="switch"
        ),
    ]
    dc_switch_ugrid1: Annotated[
        control.Valve,
        component_meta(
            yard_tag="50001069-03", component_type="valve", valve_type="switch"
        ),
    ]


class DcSimulationInputs(SimulationInputs):
    dc_brightloop_fwd1: simulation.Converter
    dc_brightloop_fwd2: simulation.Converter
    dc_ugrid1: simulation.Converter
    dc_ugrid2: simulation.Converter
    dc_brightloop_aft1: simulation.Converter
    dc_brightloop_aft2: simulation.Converter
    dc_brightloop_aft3: simulation.Converter
    dc_brightloop_aft4: simulation.Converter
    dc_seawater_supply: simulation.Boundary
    dc_dhw_supply: simulation.Boundary


class DcSimulationOutputs(SimulationValues):
    dc_seawater_return: simulation.TemperatureBoundary
    dc_dhw_exchanger: simulation.ExchangerBoundary
