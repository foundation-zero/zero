import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "High temperature",
    modeModule: "pcm",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "High temperature",
    technicalName: "high-temperature",
  }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "consumersDelta"),
    flow: getField(SensorComponentType.Flow, "consumers", "consumersFlowDhw"),
    incoming: getField(
      SensorComponentType.Temperature,
      "consumers",
      "consumersTemperatureDhwSupply",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "consumers",
      "consumersTemperatureDhwReturn",
    ),
    heatExchanger: getField(
      SensorComponentType.HeatExchanger,
      "consumers",
      "consumersDhwExchanger",
    ),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
