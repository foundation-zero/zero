import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  custom: {
    circuitName: "Fahrenheit circuit",
  },
  parameters: {},
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "boilers", "fahrenheitDelta"),
    flow: getField(SensorComponentType.Flow, "boilers", "fahrenheitFlowBoilers"),
    incoming: getField(
      SensorComponentType.Temperature,
      "boilers",
      "fahrenheitTemperatureWasteReturn",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "boilers",
      "fahrenheitTemperatureBoilersReturn",
    ),
    heatExchanger: getField(
      SensorComponentType.HeatExchanger,
      "boilers",
      "boilersFahrenheitExchanger",
    ),
  },
  tooltip: tooltip({
    title: "Fahrenheit",
    technicalName: "fahrenheit",
  }),
});
