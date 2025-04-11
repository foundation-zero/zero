from pydantic import BaseModel
from input_output.alarms import BaseAlarms, Severity, alarm


class MySensorValues(BaseModel):
    sensor: float


class MyAlarms(BaseAlarms[MySensorValues, None, None]):
    @alarm("A001", Severity.ALARM)
    def check_happiness(
        self, sensor_values: MySensorValues, control_values: None, control: None
    ) -> bool:
        return sensor_values.sensor > 5


def test_alarms():
    alarms = MyAlarms()
    sensor_values = MySensorValues(sensor=3)
    alarm_list = alarms.check(sensor_values, None, None)
    assert len(alarm_list) == 1
    assert alarm_list[0].code == "A001"
    assert alarm_list[0].severity == Severity.ALARM

    sensor_values.sensor = 10
    alarm_list = alarms.check(sensor_values, None, None)
    assert len(alarm_list) == 0
