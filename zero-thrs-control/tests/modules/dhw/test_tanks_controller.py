from thrs.control.modules.dhw import DhwParameters, TanksController
from thrs.input_output.modules.dhw import DhwSensorValues


def run_tick_boosting(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
    boosting_available: bool = True,
):
    tanks_controller(sensor_values, parameters)
    tanks_controller.apply_boosting(boosting_available)


def set_levels(sensor_values: DhwSensorValues, l1: float, l2: float, l3: float):
    sensor_values.dhw_level_tank1.level.value = l1
    sensor_values.dhw_level_tank2.level.value = l2
    sensor_values.dhw_level_tank3.level.value = l3


def set_temps(sensor_values: DhwSensorValues, t1: float, t2: float, t3: float):
    sensor_values.dhw_temperature_tank1.temperature.value = t1
    sensor_values.dhw_temperature_tank2.temperature.value = t2
    sensor_values.dhw_temperature_tank3.temperature.value = t3


def open_all_valve_setpoints(tanks_controller: TanksController):
    for tank in tanks_controller._tanks:
        tank._inlet.setpoint.value = 1.0
        tank._outlet.setpoint.value = 1.0
        tank._boosting_supply_valve.setpoint.value = 1.0
        tank._boosting_return_valve.setpoint.value = 1.0


def test_selection_all_full_all_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, none filling, none boosting
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None


def test_selection_all_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, none filling, one boosting
    set_temps(sensor_values, 60, 0, 10)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]


def test_all_full_none_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> none in use, none filling, one boosting
    set_temps(sensor_values, 0, 0, 0)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is None
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[0]


def test_none_full(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none full -> one filling, none boosting, none in use
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 100, 100, 100)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is None
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_one_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, one filling, none boosting
    set_temps(sensor_values, 0, 0, 60)
    set_levels(sensor_values, 100, 100, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[2]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_two_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, one filling, one boosting
    set_temps(sensor_values, 0, 60, 0)
    set_levels(sensor_values, 100, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]


def test_becomes_empty(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one in use -> other in use, one filling
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 270, 270, 270)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None

    set_levels(sensor_values, 10, 270, 270)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_becomes_cold(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one in use -> same in use, one boosting
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 270, 270, 270)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None

    set_temps(sensor_values, 60, 0, 60)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[1]


def test_disabling_in_use_tank_overrides_use(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one in use -> disabled, other selected in use
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 270, 270, 270)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]

    parameters = parameters.model_copy(update={"tank1_enabled": False})
    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._tanks[0]._outlet.setpoint.value == 0.0


def test_disabling_filling_tank_overrides_fill(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one filling -> disabled, other selected filling
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 100, 100, 100)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._filling_tank is tanks_controller._tanks[0]

    parameters = parameters.model_copy(update={"tank1_enabled": False})
    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._filling_tank is tanks_controller._tanks[1]
    assert tanks_controller._tanks[0]._inlet.setpoint.value == 0.0


def test_disabling_boosting_tank_overrides_boost(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one boosting -> disabled, other (cold) tank selected boosting
    set_temps(sensor_values, 60, 0, 10)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]

    parameters = parameters.model_copy(update={"tank3_enabled": False})
    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._boosting_tank is tanks_controller._tanks[1]
    assert tanks_controller._tanks[2]._boosting_supply_valve.setpoint.value == 0.0
    assert tanks_controller._tanks[2]._boosting_return_valve.setpoint.value == 0.0


def test_full_hysteresis_lower_band(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # level above lower band counts as full even below maximum
    set_temps(sensor_values, 60, 60, 60)
    set_levels(
        sensor_values,
        parameters.full_level_lower_band + 1,
        parameters.full_level_lower_band - 1,
        parameters.full_level_lower_band - 1,
    )

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is tanks_controller._tanks[1]


def test_filling_tank_not_counted_full(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 100, 100, 100)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    filling = tanks_controller._filling_tank
    assert filling is tanks_controller._tanks[0]
    assert filling is not None
    assert not filling.is_full(parameters, is_filling=True)
    assert filling.level_full(parameters) is False


def test_fresh_takeover_selects_filling_and_sweeps(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # hostile manual leaves everything open; levels call for fill on tank1
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 100, 250, 250)
    open_all_valve_setpoints(tanks_controller)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller.tank_state(
        tanks_controller._tanks[0], parameters
    ).value == "filling"
    assert tanks_controller._tanks[0]._inlet.setpoint.value == 1.0
    assert tanks_controller._tanks[0]._outlet.setpoint.value == 0.0
    # tank2 is full+hot so it becomes in-use with its outlet open; the rest
    # must be swept closed in the same tick
    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._tanks[1]._inlet.setpoint.value == 0.0
    assert tanks_controller._tanks[1]._outlet.setpoint.value == 1.0
    assert tanks_controller._tanks[2]._inlet.setpoint.value == 0.0
    assert tanks_controller._tanks[2]._outlet.setpoint.value == 0.0
    for tank in tanks_controller._tanks:
        if tank is not tanks_controller._boosting_tank:
            assert tank._boosting_supply_valve.setpoint.value == 0.0
            assert tank._boosting_return_valve.setpoint.value == 0.0


def test_fresh_takeover_selects_boosting_immediately(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # all full, one cold: boost selected first tick despite strays left open
    set_temps(sensor_values, 60, 60, 0)
    set_levels(sensor_values, 250, 250, 250)
    open_all_valve_setpoints(tanks_controller)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]
    assert tanks_controller.tank_state(
        tanks_controller._tanks[2], parameters
    ).value == "boosting"
    assert tanks_controller._tanks[2]._boosting_supply_valve.setpoint.value == 1.0
    assert tanks_controller._tanks[2]._boosting_return_valve.setpoint.value == 1.0
    for tank in tanks_controller._tanks[:2]:
        assert tank._boosting_supply_valve.setpoint.value == 0.0
        assert tank._boosting_return_valve.setpoint.value == 0.0


def test_missing_level_never_selects(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 250, 250, 250)
    run_tick_boosting(tanks_controller, sensor_values, parameters)
    assert tanks_controller._tank_in_use is not None

    tanks_controller._tanks[0].level = None
    assert tanks_controller._tanks[0].fillable(parameters) is False
    assert tanks_controller._tanks[0].level_full(parameters) is False


def test_missing_temperature_never_boosts_or_stands_by(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_levels(sensor_values, 250, 250, 250)
    set_temps(sensor_values, 60, 60, 60)
    tanks_controller(sensor_values, parameters)
    tanks_controller._tanks[0].temperature = None

    assert tanks_controller._tanks[0].standby(parameters) is False
    assert tanks_controller._tanks[0].boostable(parameters) is False
