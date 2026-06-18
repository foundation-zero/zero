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
  source: getField(SensorComponentType.HeatExchanger, "boilers", "boilersHeatpump"),
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "boilers", "heatpumpTemperatureSetpoint"),
    flow: getField(ParametersType.Flow, "boilers", "heatpumpFlowSetpoint"),
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
