import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { toFieldsMap } from "../..";
import { MimicComponentType } from "../../../../types";
import { getField } from "../../../providers";

export const BOILER_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1022": {
      custom: {
        flowSetpointName: "heatpump_flow_parameter",
        temperatureSetpointName: "heatpump_temperature_parameter",
      },
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
      parameters: {},
      sensors: {
        pump: getField(SensorComponentType.Pump, "boilers", "boilersPump"),
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
    },
  },
});
