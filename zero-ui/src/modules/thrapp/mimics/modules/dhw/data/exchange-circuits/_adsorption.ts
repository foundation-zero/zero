import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Adsorption circuit",
    modeModule: "adsorption",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "Adsorption",
    technicalName: "adsorption",
  }),
  sensors: {
    flow: getField(SensorComponentType.Flow, "adsorption", "adsorptionFlowDhw"),
    incoming: getField(
      SensorComponentType.Temperature,
      "adsorption",
      "adsorptionTemperatureWasteReturn",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "adsorption",
      "adsorptionTemperatureDhwReturn",
    ),
    heatExchanger: getField(
      SensorComponentType.HeatExchanger,
      "adsorption",
      "adsorptionDhwExchanger",
    ),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
