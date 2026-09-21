import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Adsorption circuit",
    modeModule: "adsorption",
  },
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "adsorption", "adsorptionHtExchanger"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
