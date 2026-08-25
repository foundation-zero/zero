import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.ExchangeCircuit>({
  custom: {
    circuitName: "High temperature",
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("dhw", {
      title: "High temperature",
      technicalName: "high-temperature",
    }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "consumersDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "consumersFlowDhw"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHeatpump"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "consumersTemperatureDhwSupply"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "consumersTemperatureDhwReturn"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      componentType: "Exchange circuit",
    });
  },
});
