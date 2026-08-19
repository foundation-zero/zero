from thrs.control.modules.dhw import DhwParameters, TanksController
from thrs.input_output.modules.dhw import DhwSensorValues


def test_selection_all_full_all_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, none filling, none boosting
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_temperature_tank3.temperature.value = 60

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    for tank in tanks_controller._tanks:
        tank._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None


def test_selection_all_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, none filling, one boosting
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_temperature_tank2.temperature.value = 0
    sensor_values.dhw_temperature_tank3.temperature.value = 10

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    for tank in tanks_controller._tanks:
        tank._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]


def test_all_full_none_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> none in use, none filling, one boosting
    sensor_values.dhw_temperature_tank1.temperature.value = 0
    sensor_values.dhw_temperature_tank2.temperature.value = 0
    sensor_values.dhw_temperature_tank3.temperature.value = 0

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    for tank in tanks_controller._tanks:
        tank._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is None
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[0]


def test_none_full(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none full -> one filling, none boosting, none in use
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_temperature_tank3.temperature.value = 60

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is None
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_one_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, one filling, none boosting
    sensor_values.dhw_temperature_tank1.temperature.value = 0
    sensor_values.dhw_temperature_tank2.temperature.value = 0
    sensor_values.dhw_temperature_tank3.temperature.value = 60

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    tanks_controller._tanks[2]._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[2]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_two_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # none in use -> one in use, one filling, one boosting
    sensor_values.dhw_temperature_tank1.temperature.value = 0
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_temperature_tank3.temperature.value = 0

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    tanks_controller._tanks[1]._full = True
    tanks_controller._tanks[2]._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]


def test_becomes_empty(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one in use -> other in use, one filling
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_level_tank1.level.value = 270
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_level_tank2.level.value = 270
    sensor_values.dhw_temperature_tank3.temperature.value = 60
    sensor_values.dhw_level_tank3.level.value = 270

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    for tank in tanks_controller._tanks:
        tank._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None

    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_level_tank1.level.value = 10
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_level_tank2.level.value = 270
    sensor_values.dhw_temperature_tank3.temperature.value = 60
    sensor_values.dhw_level_tank3.level.value = 270

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_becomes_cold(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one in use -> same in use, one boosting
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_level_tank1.level.value = 270
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_level_tank2.level.value = 270
    sensor_values.dhw_temperature_tank3.temperature.value = 60
    sensor_values.dhw_level_tank3.level.value = 270

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    for tank in tanks_controller._tanks:
        tank._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None

    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_temperature_tank2.temperature.value = 0
    sensor_values.dhw_temperature_tank3.temperature.value = 60

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[1]


def test_disabling_in_use_tank_overrides_use(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one in use -> disabled, other selected in use
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_level_tank1.level.value = 270
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_level_tank2.level.value = 270
    sensor_values.dhw_temperature_tank3.temperature.value = 60
    sensor_values.dhw_level_tank3.level.value = 270

    # set _full as it does not depend on the tank level but on whether the tank has been filled
    for tank in tanks_controller._tanks:
        tank._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]

    parameters = parameters.model_copy(update={"tank1_enabled": False})
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._tanks[0]._outlet.setpoint.value == 0.0


def test_disabling_filling_tank_overrides_fill(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one filling -> disabled, other selected filling
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_temperature_tank2.temperature.value = 60
    sensor_values.dhw_temperature_tank3.temperature.value = 60

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._filling_tank is tanks_controller._tanks[0]

    parameters = parameters.model_copy(update={"tank1_enabled": False})
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._filling_tank is tanks_controller._tanks[1]
    assert tanks_controller._tanks[0]._inlet.setpoint.value == 0.0


def test_disabling_boosting_tank_overrides_boost(
    tanks_controller: TanksController,
    sensor_values: DhwSensorValues,
    parameters: DhwParameters,
):
    # one boosting -> disabled, other (cold) tank selected boosting
    sensor_values.dhw_temperature_tank1.temperature.value = 60
    sensor_values.dhw_temperature_tank2.temperature.value = 0
    sensor_values.dhw_temperature_tank3.temperature.value = 10

    for tank in tanks_controller._tanks:
        tank._full = True

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]

    parameters = parameters.model_copy(update={"tank3_enabled": False})
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._boosting_tank is tanks_controller._tanks[1]
    assert tanks_controller._tanks[2]._boosting_supply_valve.setpoint.value == 0.0
    assert tanks_controller._tanks[2]._boosting_return_valve.setpoint.value == 0.0
