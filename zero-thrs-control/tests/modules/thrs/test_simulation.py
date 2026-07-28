from collections.abc import Callable
from datetime import datetime, timedelta
from typing import cast

import pytest
from pytest import fixture

from tests.helpers.simulation_inputs import simulator_input_field_setters
from tests.simulation.test_cosimulation import MockFmu
from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.adsorption import (
    ADSORPTION_MODULE_DESCRIPTION,
    AdsorptionParameters,
)
from thrs.control.modules.consumers import (
    CONSUMERS_MODULE_DESCRIPTION,
    ConsumersParameters,
)
from thrs.control.modules.dc import DC_MODULE_DESCRIPTION, DcParameters
from thrs.control.modules.dhw import DHW_MODULE_DESCRIPTION, DhwParameters
from thrs.control.modules.drives import DRIVES_MODULE_DESCRIPTION, DrivesParameters
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION, PcmParameters
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION, PvtParameters
from thrs.control.modules.thrusters import (
    THRUSTERS_MODULE_DESCRIPTION,
    ThrustersParameters,
)
from thrs.input_output.base import CombinedValues, Stamped
from thrs.input_output.definitions.simulation import (
    AdsorptionChiller,
    Boundary,
    Converter,
    FlowBoundary,
    HeatSource,
    HvacExchanger,
    OverpressureTemperatureBoundary,
    Pcs,
    PropulsionDrive,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.adsorption import (
    AdsorptionSensorValues,
)
from thrs.input_output.modules.consumers import (
    ConsumersSensorValues,
)
from thrs.input_output.modules.dc import DcSensorValues
from thrs.input_output.modules.dhw import DhwSensorValues
from thrs.input_output.modules.drives import DrivesSensorValues
from thrs.input_output.modules.pcm import PcmSensorValues
from thrs.input_output.modules.pvt import PvtSensorValues
from thrs.input_output.modules.thrs import (
    ThrsSimulationInputs,
    ThrsSimulationOutputs,
    participants,
)
from thrs.input_output.modules.thrusters import ThrustersSensorValues
from thrs.orchestration.module import ModuleClassMap, ModuleDescription
from thrs.orchestration.simulation import Simulation
from thrs.simulation.cosimulation import CoSimulationMaster, CoSimulationParticipant
from thrs.simulation.io_mapping import CombinedIoMapping


@fixture
def simulation_inputs() -> ThrsSimulationInputs:
    return ThrsSimulationInputs(
        thrusters_thruster_aft=Thruster(
            heat_flow=Stamped.stamp(9000), active=Stamped.stamp(True)
        ),
        thrusters_thruster_fwd=Thruster(
            heat_flow=Stamped.stamp(4300), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(16000)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(8000)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(32), flow=Stamped.stamp(64)
        ),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
        adsorption_cooling_supply=TemperatureBoundary(temperature=Stamped.stamp(20.0)),
        adsorption_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
        ),
        adsorption_available_hot_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(65.0)
        ),
        adsorption_available_cold_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(20.0)
        ),
        adsorption_available_seawater_temperature=TemperatureBoundary(
            temperature=Stamped.stamp(30.0)
        ),
        adsorption_chiller=AdsorptionChiller(free_cooling=Stamped.stamp(False)),
        dhw_freshwater_supply=OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(20), overpressure=Stamped.stamp(0.1)
        ),
        dhw_hvac_exchanger=HvacExchanger(
            heat_flow=Stamped.stamp(300), maximum_temperature=Stamped.stamp(35)
        ),
        dhw_seawater_supply=TemperatureBoundary(temperature=Stamped.stamp(32)),
        dhw_hotwater_demand=FlowBoundary(flow=Stamped.stamp(20)),
        dc_brightloop_fwd1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_fwd2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_ugrid1=Converter(heat_flow=Stamped.stamp(2000), active=Stamped.stamp(True)),
        dc_ugrid2=Converter(heat_flow=Stamped.stamp(2000), active=Stamped.stamp(True)),
        dc_brightloop_aft1=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft2=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft3=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_brightloop_aft4=Converter(
            heat_flow=Stamped.stamp(500), active=Stamped.stamp(True)
        ),
        dc_seawater_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(64)
        ),
        drives_oil_cooler_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_oil_cooler_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        drives_propdrive_aft1=PropulsionDrive(
            heat_flow=Stamped.stamp(2800), active=Stamped.stamp(True)
        ),
        drives_propdrive_aft2=PropulsionDrive(
            heat_flow=Stamped.stamp(2800), active=Stamped.stamp(True)
        ),
        drives_propdrive_fwd1=PropulsionDrive(
            heat_flow=Stamped.stamp(1250), active=Stamped.stamp(True)
        ),
        drives_propdrive_fwd2=PropulsionDrive(
            heat_flow=Stamped.stamp(1250), active=Stamped.stamp(True)
        ),
        drives_shorepower=Converter(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_seawater_supply=Boundary(
            temperature=Stamped.stamp(20), flow=Stamped.stamp(64)
        ),
    )


@fixture
def modules() -> dict[str, ModuleDescription]:
    return {
        "thrusters": THRUSTERS_MODULE_DESCRIPTION,
        "pvt": PVT_MODULE_DESCRIPTION,
        "pcm": PCM_MODULE_DESCRIPTION,
        "consumers": CONSUMERS_MODULE_DESCRIPTION,
        "adsorption": ADSORPTION_MODULE_DESCRIPTION,
        "dhw": DHW_MODULE_DESCRIPTION,
        "dc": DC_MODULE_DESCRIPTION,
        "drives": DRIVES_MODULE_DESCRIPTION,
    }


@fixture
def control() -> Callable[[CombinedValues], tuple[CombinedValues, CombinedValues]]:
    state_logger = MachineStateLoggingServiceNoop()
    modules = {
        "thrusters": THRUSTERS_MODULE_DESCRIPTION.control(
            ThrustersParameters(), datetime.now, state_logger
        ),
        "pvt": PVT_MODULE_DESCRIPTION.control(
            PvtParameters(), datetime.now, state_logger
        ),
        "pcm": PCM_MODULE_DESCRIPTION.control(
            PcmParameters(), datetime.now, state_logger
        ),
        "consumers": CONSUMERS_MODULE_DESCRIPTION.control(
            ConsumersParameters(), datetime.now, state_logger
        ),
        "adsorption": ADSORPTION_MODULE_DESCRIPTION.control(
            AdsorptionParameters(), datetime.now, state_logger
        ),
        "dhw": DHW_MODULE_DESCRIPTION.control(
            DhwParameters(), datetime.now, state_logger
        ),
        "dc": DC_MODULE_DESCRIPTION.control(DcParameters(), datetime.now, state_logger),
        "drives": DRIVES_MODULE_DESCRIPTION.control(
            DrivesParameters(), datetime.now, state_logger
        ),
    }

    def control(sensor_values: CombinedValues) -> tuple[CombinedValues, CombinedValues]:
        combined_control_values = CombinedValues({})
        combined_controller_state = CombinedValues({})

        for name, module in modules.items():
            sensors = sensor_values.values.get(name, None)
            if sensors:
                control_value, controller_state = module.control(sensors)
            else:
                control_value, controller_state = module.initial()

            combined_control_values.values[name] = control_value
            combined_controller_state.values[name] = controller_state

        return (combined_control_values, combined_controller_state)

    return control


@fixture(
    params=list(
        simulator_input_field_setters(
            ThrsSimulationInputs,
            ignore=[
                "adsorption_available_hot_temperature",
                "adsorption_available_cold_temperature",
                "adsorption_available_seawater_temperature",
                "adsorption_chiller",
            ],
        )
    )
)
def incorrect_simulation_inputs(simulation_inputs, request):
    inputs = simulation_inputs.get_values_at_time(datetime.now())
    request.param(inputs, -9e7)
    return inputs


@fixture()
def thrs_sensor_values() -> ModuleClassMap:
    return {
        "thrusters": ThrustersSensorValues,
        "pvt": PvtSensorValues,
        "pcm": PcmSensorValues,
        "consumers": ConsumersSensorValues,
        "adsorption": AdsorptionSensorValues,
        "dhw": DhwSensorValues,
        "dc": DcSensorValues,
        "drives": DrivesSensorValues,
    }


def test_thrs_simulation_inputs(
    control, thrs_sensor_values, incorrect_simulation_inputs
):
    with CoSimulationMaster(participants) as fmu:
        simulation = Simulation(
            thrs_sensor_values,
            ThrsSimulationOutputs,
            fmu,
            incorrect_simulation_inputs,
            datetime.now(),
            timedelta(seconds=1),
        )

        with pytest.raises(Exception):
            for _ in range(120):
                simulation.tick(control(CombinedValues({}))[0])


def test_thrs_cosimulation_coupling_routes_previous_outputs(
    control, thrs_sensor_values, simulation_inputs
):
    mock_fmus = [
        MockFmu(
            {
                output_key: float(index + 1)
                for output_key in participant.fmu_key_output_mapping.values()
            }
        )
        for index, participant in enumerate(participants)
    ]

    mock_participants = [
        CoSimulationParticipant(
            lambda mock=mock_fmus[index]: mock,
            participant.sensor_values_clss,
            participant.control_values_clss,
            participant.simulation_inputs_cls,
            participant.simulation_outputs_cls,
            list(participant.couplings),
        )
        for index, participant in enumerate(participants)
    ]

    thrs_master = CoSimulationMaster(mock_participants)

    io_mapping = CombinedIoMapping(thrs_sensor_values, ThrsSimulationOutputs)
    control_values = control(CombinedValues({}))[0]

    inputs = io_mapping.generate_inputs(control_values, simulation_inputs)

    thrs_master.tick(inputs, duration=timedelta(seconds=1))

    thrs_master.tick(inputs, duration=timedelta(seconds=1))

    drives_participant = thrs_master._participants[4]
    dhw_mock = cast(MockFmu, mock_participants[2].fmu)
    drives_mock = cast(MockFmu, mock_participants[4].fmu)

    drives_dhw_supply_temperature_key = drives_participant.fmu_key_input_mapping[
        ("drives_dhw_supply", "temperature")
    ]
    drives_dhw_supply_flow_key = drives_participant.fmu_key_input_mapping[
        ("drives_dhw_supply", "flow")
    ]

    dhw_drives_exchanger_temperature_key = thrs_master.total_fmu_key_output_mapping[
        ("dhw_drives_exchanger", "temperature_supply")
    ]
    dhw_drives_exchanger_flow_key = thrs_master.total_fmu_key_output_mapping[
        ("dhw_drives_exchanger", "flow")
    ]

    # First tick uses coupling defaults
    assert drives_mock.inputs[0][drives_dhw_supply_temperature_key] == 30.0
    assert drives_mock.inputs[0][drives_dhw_supply_flow_key] == 0.0

    # Second tick uses previous DHW participant outputs
    assert (
        drives_mock.inputs[1][drives_dhw_supply_temperature_key]
        == dhw_mock._outputs[dhw_drives_exchanger_temperature_key]
    )
    assert (
        drives_mock.inputs[1][drives_dhw_supply_flow_key]
        == dhw_mock._outputs[dhw_drives_exchanger_flow_key]
    )
