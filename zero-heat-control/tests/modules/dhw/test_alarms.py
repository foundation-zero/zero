from thrs.control.modules.dhw import DhwAlarms, DhwControllerState, DhwParameters
from thrs.input_output.definitions.units import TankState
from thrs.input_output.modules.dhw import DhwControlValues, DhwSensorValues

WARNING_CODE = "Tank in use below minimum temperature"


def controller_state(tank1_state: TankState) -> DhwControllerState:
    state = DhwControllerState.zero()
    state.dhw_tanks_controller.tank1_state.value = tank1_state
    state.dhw_tanks_controller.tank2_state.value = TankState.STANDBY
    state.dhw_tanks_controller.tank3_state.value = TankState.STANDBY
    return state


def test_cold_tank_in_use_raises_warning(
    alarms: DhwAlarms,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    sensor_values.dhw_temperature_tank1.temperature.value = (
        parameters.minimum_tank_temperature - 5
    )

    raised = alarms.check(
        sensor_values,
        DhwControlValues.zero(),
        parameters,
        controller_state(TankState.IN_USE),
    )

    warning = next(alarm for alarm in raised if alarm.code == WARNING_CODE)
    assert "no other tank is available" in warning.message


def test_hot_tank_in_use_raises_no_warning(
    alarms: DhwAlarms,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    sensor_values.dhw_temperature_tank1.temperature.value = (
        parameters.minimum_tank_temperature + 5
    )

    raised = alarms.check(
        sensor_values,
        DhwControlValues.zero(),
        parameters,
        controller_state(TankState.IN_USE),
    )

    assert not [alarm for alarm in raised if alarm.code == WARNING_CODE]


def test_cold_tank_not_in_use_raises_no_warning(
    alarms: DhwAlarms,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    sensor_values.dhw_temperature_tank1.temperature.value = (
        parameters.minimum_tank_temperature - 5
    )

    raised = alarms.check(
        sensor_values,
        DhwControlValues.zero(),
        parameters,
        controller_state(TankState.NEEDS_BOOST),
    )

    assert not [alarm for alarm in raised if alarm.code == WARNING_CODE]
