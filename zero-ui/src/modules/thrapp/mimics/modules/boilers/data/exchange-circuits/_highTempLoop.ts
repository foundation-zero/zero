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
    deltaT: getField(SensorComponentType.DeltaT, "boilers", "consumersDelta"),
    flow: getField(SensorComponentType.Flow, "boilers", "consumersFlowBoosting"),
    incoming: getField(
      SensorComponentType.Temperature,
      "boilers",
      "consumersTemperatureBoostingSupply",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "boilers",
      "consumersTemperatureBoostingReturn",
    ),
  },
  tooltip: tooltip({
    title: "High Temp Loop",
    technicalName: "high-temp-loop",
  }),
});
