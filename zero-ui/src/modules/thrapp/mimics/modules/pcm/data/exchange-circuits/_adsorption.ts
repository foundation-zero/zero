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
  source: getCustomField("pcm", {
    title: "Adsorption",
    technicalName: "adsorption",
  }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "adsorption", "placeholder"),
    flow: getField(SensorComponentType.Flow, "adsorption", "adsorptionFlowHt"),
    incoming: getField(
      SensorComponentType.Temperature,
      "adsorption",
      "adsorptionTemperatureHtReturn",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "adsorption",
      "adsorptionTemperatureHtSupply",
    ),
    heatExchanger: getField(
      SensorComponentType.HeatExchanger,
      "adsorption",
      "adsorptionHtExchanger",
    ),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
