import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "High temperature",
  },
  parameters: {},
  source: getCustomField("dhw", "high-temperature"),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "consumersDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "consumersFlowDhw"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "consumersTemperatureDhwSupply"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "consumersTemperatureDhwReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHeatpump"),
  },
  tooltip: tooltip({
    title: "High temperature",
    technicalName: "high-temperature",
  }),
});
