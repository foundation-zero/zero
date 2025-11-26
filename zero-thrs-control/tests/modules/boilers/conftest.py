from datetime import datetime, timedelta
from pytest import fixture

from thrs.control.modules.boilers import BoilersParameters, Tank, TanksController
from thrs.input_output.modules.boilers import BoilersControlValues, BoilersSensorValues


class TestTime:
    def __init__(self, duration: timedelta = timedelta(seconds=1)):
        self._time = datetime.now()
        self._duration = duration

    def time(self) -> datetime:
        self._time += self._duration
        return self._time


@fixture
def parameters() -> BoilersParameters:
    return BoilersParameters()


@fixture
def sensor_values() -> BoilersSensorValues:
    return BoilersSensorValues.zero()


@fixture
def tanks_controller(test_time, parameters) -> TanksController:
    control_values = BoilersControlValues.zero()
    return TanksController(
        tank1=Tank(
            fill_valve=control_values.boilers_switch_tank1_fill,
            empty_valve=control_values.boilers_switch_tank1_empty,
            boosting_supply_valve=control_values.boilers_switch_tank1_boosting_supply,
            boosting_return_valve=control_values.boilers_switch_tank1_boosting_return,
            disabled=parameters.tank1_disabled,
        ),
        tank2=Tank(
            fill_valve=control_values.boilers_switch_tank2_fill,
            empty_valve=control_values.boilers_switch_tank2_empty,
            boosting_supply_valve=control_values.boilers_switch_tank2_boosting_supply,
            boosting_return_valve=control_values.boilers_switch_tank2_boosting_return,
            disabled=parameters.tank2_disabled,
        ),
        tank3=Tank(
            fill_valve=control_values.boilers_switch_tank3_fill,
            empty_valve=control_values.boilers_switch_tank3_empty,
            boosting_supply_valve=control_values.boilers_switch_tank3_boosting_supply,
            boosting_return_valve=control_values.boilers_switch_tank3_boosting_return,
            disabled=parameters.tank3_disabled,
        ),
        time_fn=test_time.time,
    )


@fixture()
def test_time() -> TestTime:
    return TestTime()
