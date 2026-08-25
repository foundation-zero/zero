import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.ExchangeCircuit>({
  custom: {
    circuitName: "DC Converters",
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("dhw", {
      title: "DC converters",
      technicalName: "dc-converters",
    }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "dcDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "dcFlowRecovery"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDcExchanger"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dcTemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dcTemperatureRecoveryReturn"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      componentType: "Exchange circuit",
    });
  },
});
