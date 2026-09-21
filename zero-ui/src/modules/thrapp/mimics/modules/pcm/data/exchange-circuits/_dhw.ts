import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Domestic hot water",
    modeModule: "dhw",
  },
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwConsumersExchanger"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
