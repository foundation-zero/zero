import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";

export default toInstance<MimicComponentType.Pump>({
  custom: {},
  source: getField(SensorComponentType.Pump, "boilers", "boilersPump"),
  controls: {
    flowController: getField(
      ControlComponentType.PIDController,
      "boilers",
      "boilersPumpFlowController",
    ),
    temperatureController: getField(
      ControlComponentType.PIDController,
      "boilers",
      "boilersPumpTemperatureController",
    ),
    pump: getField(ControlComponentType.Pump, "boilers", "boilersPump"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "boilers", "heatpumpFlowSetpoint"),
    temperature: getField(ParametersType.Temperature, "boilers", "heatpumpTemperatureSetpoint"),
  },
  sensors: {
    pressure: getField(SensorComponentType.Pressure, "boilers", "boilersPressureBoosting"),
    flowMeasurement: getField(SensorComponentType.Flow, "boilers", "boilersFlowBoosting"),
    temperatureMeasurement: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureBoostingReturn",
    ),
  },
  tooltip: {
    title: "Pump",
    itemName: "Circulation pump Hot freshwater",
    technicalName: "boilers-pump",
    yardTag: "1022",
  },
});
