import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  custom: {
    circuitName: "High Temp Loop circuit",
  },
  parameters: {},
  source: undefined,
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "consumersDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "consumersFlowDhw"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "consumersTemperatureDhwSupply"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "consumersTemperatureDhwReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHeatpump"),
  },
  tooltip: tooltip({
    title: "High Temp Loop",
    technicalName: "high-temp-loop",
  }),
});
