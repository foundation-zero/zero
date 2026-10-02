import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.ConnectingCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Thrusters",
    modeModule: "thrusters",
  },
  parameters: {},
  source: getField(SensorComponentType.HeatTransferDevice, "thrusters", "thrustersPcmHeat"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Connecting circuit",
      componentType: "Thrusters loop",
    });
  },
});
