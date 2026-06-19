import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";

export default toInstance<MimicComponentType.Pump>({
  custom: {},
  source: getField(SensorComponentType.Pump, "dhw", "dhwPump"),
  controls: {
    flowController: getField(ControlComponentType.PIDController, "dhw", "dhwPumpFlowController"),
    temperatureController: getField(
      ControlComponentType.PIDController,
      "dhw",
      "dhwPumpTemperatureController",
    ),
    pump: getField(ControlComponentType.Pump, "dhw", "dhwPump"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
    temperature: getField(ParametersType.Temperature, "dhw", "heatpumpTemperatureSetpoint"),
  },
  sensors: {
    pressure: getField(SensorComponentType.Pressure, "dhw", "dhwPressure"),
    flowMeasurement: getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting"),
    temperatureMeasurement: getField(
      SensorComponentType.Temperature,
      "dhw",
      "dhwTemperatureBoostingReturn",
    ),
  },
  tooltip: {
    title: "Pump",
    itemName: "Circulation pump Hot freshwater",
    technicalName: "dhw-pump",
    yardTag: "1022",
  },
});
