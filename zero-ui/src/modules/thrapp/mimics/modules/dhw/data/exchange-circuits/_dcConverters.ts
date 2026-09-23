import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "DC Converters",
    modeModule: "dc",
  },
  parameters: {},
  source: getField(SensorComponentType.HeatTransferDevice, "dc", "dcDhwExchanger"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
