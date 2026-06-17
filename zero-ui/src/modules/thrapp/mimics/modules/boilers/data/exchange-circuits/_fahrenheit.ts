import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  custom: {},
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
  },
  tooltip: tooltip({
    title: "Fahrenheit",
    technicalName: "fahrenheit",
  }),
});
