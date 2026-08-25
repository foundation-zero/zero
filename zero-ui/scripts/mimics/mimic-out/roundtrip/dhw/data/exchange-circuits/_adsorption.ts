import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.ExchangeCircuit>({
  custom: {
    circuitName: "Adsorption circuit",
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("dhw", {
      title: "Adsorption",
      technicalName: "adsorption",
    }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "adsorptionDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "adsorptionFlowDhw"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwAdsorptionExchanger"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "adsorptionTemperatureWasteReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "adsorptionTemperatureDhwReturn"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      componentType: "Exchange circuit",
    });
  },
});
