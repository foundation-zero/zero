import pytest
from thrs.control.modules.boilers import BoilersParameters, TanksController
from thrs.input_output.modules.boilers import BoilersSensorValues

pytest.skip(
    allow_module_level=True
)  # Skip as long as boiler module is not implemented yet


def test_selection_all_full_all_hot(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # none in use -> one in use, none filling, none boosting
    sensor_values.boilers_temperature_tank1.temperature.value = 60
    sensor_values.boilers_level_tank1.level.value = 270
    sensor_values.boilers_temperature_tank2.temperature.value = 60
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 60
    sensor_values.boilers_level_tank3.level.value = 270

    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None


def test_selection_all_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # none in use -> one in use, none filling, one boosting
    sensor_values.boilers_temperature_tank1.temperature.value = 60
    sensor_values.boilers_level_tank1.level.value = 270
    sensor_values.boilers_temperature_tank2.temperature.value = 0
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 10
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]


def test_selection_all_full_none_hot(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # none in use -> none in use, none filling, one boosting
    sensor_values.boilers_temperature_tank1.temperature.value = 0
    sensor_values.boilers_level_tank1.level.value = 270
    sensor_values.boilers_temperature_tank2.temperature.value = 0
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 0
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is None
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[0]


def test_selection_none_full(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # none full -> one filling, none boosting, none in use
    sensor_values.boilers_temperature_tank1.temperature.value = 60
    sensor_values.boilers_level_tank1.level.value = 10
    sensor_values.boilers_temperature_tank2.temperature.value = 60
    sensor_values.boilers_level_tank2.level.value = 10
    sensor_values.boilers_temperature_tank3.temperature.value = 60
    sensor_values.boilers_level_tank3.level.value = 10
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is None
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_selection_one_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # none in use -> one in use, one filling, none boosting
    sensor_values.boilers_temperature_tank1.temperature.value = 0
    sensor_values.boilers_level_tank1.level.value = 10
    sensor_values.boilers_temperature_tank2.temperature.value = 0
    sensor_values.boilers_level_tank2.level.value = 10
    sensor_values.boilers_temperature_tank3.temperature.value = 60
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[2]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_selection_two_full_one_hot(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # none in use -> one in use, one filling, one boosting
    sensor_values.boilers_temperature_tank1.temperature.value = 0
    sensor_values.boilers_level_tank1.level.value = 10
    sensor_values.boilers_temperature_tank2.temperature.value = 60
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 0
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is tanks_controller._tanks[2]


@pytest.mark.skip(reason="Need criterium for when tank is empty")
def test_selection_becomes_empty(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # one in use -> other in use, one filling
    sensor_values.boilers_temperature_tank1.temperature.value = 60
    sensor_values.boilers_level_tank1.level.value = 270
    sensor_values.boilers_temperature_tank2.temperature.value = 60
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 60
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None

    sensor_values.boilers_temperature_tank1.temperature.value = 60
    sensor_values.boilers_level_tank1.level.value = 10
    sensor_values.boilers_temperature_tank2.temperature.value = 60
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 60
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[1]
    assert tanks_controller._filling_tank is tanks_controller._tanks[0]
    assert tanks_controller._boosting_tank is None


def test_selection_becomes_cold(
    tanks_controller: TanksController,
    sensor_values: BoilersSensorValues,
    parameters: BoilersParameters,
):
    # one in use -> same in use, one boosting
    sensor_values.boilers_temperature_tank1.temperature.value = 60
    sensor_values.boilers_level_tank1.level.value = 270
    sensor_values.boilers_temperature_tank2.temperature.value = 60
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 60
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is None

    sensor_values.boilers_temperature_tank1.temperature.value = 60
    sensor_values.boilers_level_tank1.level.value = 270
    sensor_values.boilers_temperature_tank2.temperature.value = 0
    sensor_values.boilers_level_tank2.level.value = 270
    sensor_values.boilers_temperature_tank3.temperature.value = 60
    sensor_values.boilers_level_tank3.level.value = 270
    tanks_controller(sensor_values, parameters)

    assert tanks_controller._tank_in_use is tanks_controller._tanks[0]
    assert tanks_controller._filling_tank is None
    assert tanks_controller._boosting_tank is tanks_controller._tanks[1]
