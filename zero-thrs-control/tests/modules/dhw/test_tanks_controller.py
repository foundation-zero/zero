from thrs.control.modules.dhw import DhwParameters, TanksController
from thrs.input_output.definitions.units import TankState
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
    # none in use -> fallback keeps the warmest (tie: tank1) in use, next boosts
    set_temps(sensor_values, 0, 0, 0)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[1]


def test_none_full(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none full but hot -> fallback keeps warmest (tie: tank1) in use; next fills
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 100, 100, 100)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is tanks_controller._tanks[1]
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
    # one filling -> disabled, other selected filling. tank1 is the fallback
    # in-use tank (warmest, tie), so tank2 is the one filling.
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 100, 100, 100)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._filling_tank is tanks_controller._tanks[1]

    parameters = parameters.model_copy(update={"tank2_enabled": False})
    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._filling_tank is tanks_controller._tanks[2]
    assert tanks_controller._tanks[1]._inlet.setpoint.value == 0.0


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

    # tank1 is the fallback in-use tank (warmest, tie), so tank2 fills.
    filling = tanks_controller._filling_tank
    assert filling is tanks_controller._tanks[1]
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
    assert (
        tanks_controller.tank_state(tanks_controller._tanks[0], parameters).value
        == "filling"
    )
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
    assert (
        tanks_controller.tank_state(tanks_controller._tanks[2], parameters).value
        == "boosting"
    )
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


def test_boosting_follows_full_level_bound_changes(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 60, 60, 0)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    boosting_tank = tanks_controller._tanks[2]
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]

    increased_fill_minimum = parameters.model_copy(
        update={"full_level_lower_band": 255}
    )
    run_tick_boosting(tanks_controller, sensor_values, increased_fill_minimum)

    assert tanks_controller._boosting_tank is None
    assert boosting_tank._boosting_supply_valve.setpoint.value == 0.0
    assert boosting_tank._boosting_return_valve.setpoint.value == 0.0

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._boosting_tank is boosting_tank


def test_in_use_hands_over_when_it_goes_cold(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]

    set_temps(sensor_values, 40, 60, 60)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._tanks[0]._outlet.setpoint.value == 0.0
    assert tanks_controller._tanks[1]._outlet.setpoint.value == 1.0
    assert tanks_controller._boosting_tank is tanks_controller._tanks[0]


def test_in_use_kept_when_cold_without_replacement(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 60, 40, 40)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    in_use = tanks_controller._tanks[0]
    assert tanks_controller._tank_in_use is in_use

    set_temps(sensor_values, 40, 40, 40)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is in_use
    assert in_use._outlet.setpoint.value == 1.0
    assert tanks_controller.tank_state(in_use, parameters) is TankState.IN_USE


def test_lowering_minimum_temperature_keeps_tank_in_use(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 60, 60, 60)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    in_use = tanks_controller._tank_in_use
    assert in_use is tanks_controller._tanks[0]
    assert in_use is not None

    # No tank clears the raised minimum, so there is nothing to hand over to.
    increased_temperature_minimum = parameters.model_copy(
        update={"minimum_tank_temperature": 70, "maximum_tank_temperature": 75}
    )
    run_tick_boosting(tanks_controller, sensor_values, increased_temperature_minimum)

    assert tanks_controller._tank_in_use is in_use
    assert (
        tanks_controller.tank_state(in_use, increased_temperature_minimum)
        is TankState.IN_USE
    )

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is in_use
    assert in_use._outlet.setpoint.value == 1.0
    assert tanks_controller.tank_state(in_use, parameters) is TankState.IN_USE


def test_raising_minimum_temperature_hands_over_in_use_tank(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 56, 60, 60)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]

    increased_temperature_minimum = parameters.model_copy(
        update={"minimum_tank_temperature": 58}
    )
    run_tick_boosting(tanks_controller, sensor_values, increased_temperature_minimum)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._tanks[0]._outlet.setpoint.value == 0.0
    assert tanks_controller._tanks[1]._outlet.setpoint.value == 1.0
    assert tanks_controller._boosting_tank is tanks_controller._tanks[0]


def test_fallback_warmest_non_empty_ignores_full(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # No standby: a partial-but-hot tank is preferred over a full-but-cold one.
    set_temps(sensor_values, 20, 58, 20)
    set_levels(sensor_values, 250, 100, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]


def test_fallback_takes_over_boosting_tank(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # tank1 hot (in use), tank2 warmer-cold (boosting), tank3 coldest.
    set_temps(sensor_values, 60, 40, 20)
    set_levels(sensor_values, 250, 250, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is tanks_controller._tanks[1]

    # Disabling the in-use tank leaves no standby, so the fallback takes over the
    # warmest remaining tank - the boosting one - and stops its boost.
    disabled_tank1 = parameters.model_copy(update={"tank1_enabled": False})
    run_tick_boosting(tanks_controller, sensor_values, disabled_tank1)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._tanks[1]._outlet.setpoint.value == 1.0
    assert tanks_controller._tanks[1]._boosting_supply_valve.setpoint.value == 0.0
    assert tanks_controller._tanks[1]._boosting_return_valve.setpoint.value == 0.0
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]


def test_fallback_takes_over_filling_tank(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # tank1 hot+full (in use), tank2 hot+partial (filling), tank3 empty.
    set_temps(sensor_values, 60, 58, 20)
    set_levels(sensor_values, 250, 100, 10)

    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is tanks_controller._tanks[1]

    # tank1 empties, no standby: the fallback takes over the warmest remaining
    # tank, which is the one that was filling; another tank takes the fill slot.
    set_levels(sensor_values, 10, 100, 10)
    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._tanks[1]._outlet.setpoint.value == 1.0
    assert tanks_controller._filling_tank is not tanks_controller._tanks[1]


def test_fallback_does_not_preempt_cold_in_use_with_hotter_partial(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 60, 58, 20)
    set_levels(sensor_values, 250, 100, 250)

    run_tick_boosting(tanks_controller, sensor_values, parameters)
    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]

    # tank1 goes cold; tank2 is hotter but not full (not a standby replacement),
    # so the serving tank is kept rather than preempted by the fallback.
    set_temps(sensor_values, 40, 58, 20)
    run_tick_boosting(tanks_controller, sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._tanks[0]._outlet.setpoint.value == 1.0


def test_fallback_excludes_disabled_and_unknown_temperature(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    set_temps(sensor_values, 40, 40, 40)
    set_levels(sensor_values, 250, 250, 250)
    tanks_controller(sensor_values, parameters)

    # tank1 disabled and tank3 temperature unknown, so only tank2 is eligible.
    tanks_controller._tanks[0].enabled = False
    tanks_controller._tanks[2].temperature = None

    assert (
        tanks_controller._fallback_tank_in_use(parameters)
        is (tanks_controller._tanks[1])
    )
