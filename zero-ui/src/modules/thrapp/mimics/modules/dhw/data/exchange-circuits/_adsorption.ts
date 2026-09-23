import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Adsorption",
    modeModule: "adsorption",
  },
  parameters: {},
  source: getField(SensorComponentType.HeatTransferDevice, "adsorption", "adsorptionDhwExchanger"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
