import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatPump>({
  controls: {
    heatExchanger: getField(ControlComponentType.Heatpump, "boilers", "boilersHeatpump"),
    controller: getField(
      ControlComponentType.PIDController,
      "boilers",
      "boilersPumpFlowController",
    ),
  },
  custom: {
    controllerName: "Pump flow controller",
    setpointName: "Heatpump flow parameter",
  },
  parameters: {
    temperature: getField(ParametersType.Temperature, "boilers", "heatpumpTemperatureSetpoint"),
  },
  sensors: {
    heatExchanger: getField(SensorComponentType.HeatExchanger, "boilers", "boilersHeatpump"),
    incoming: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureBoostingReturn",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureBoostingSupply",
    ),
    measurement: getField(SensorComponentType.Flow, "boilers", "boilersFlowBoosting"),
  },
  tooltip: tooltip({
    title: "Heat Pump",
    yardTag: "1035",
    technicalName: "boilers-heatpump",
  }),
});
