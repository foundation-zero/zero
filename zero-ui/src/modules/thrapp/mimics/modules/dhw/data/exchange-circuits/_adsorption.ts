import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Adsorption circuit",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "Adsorption",
    technicalName: "adsorption",
  }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "adsorptionDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "adsorptionFlowDhw"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "adsorptionTemperatureWasteReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "adsorptionTemperatureDhwReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwAdsorptionExchanger"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
