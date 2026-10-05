import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.ConnectingCircuit>({
  controls: {},
  controllerState: {},
  custom: { circuitName: "PCM", modeModule: "pcm" },
  parameters: {},
  source: getField(SensorComponentType.HeatTransferDevice, "thrusters", "thrustersPcmHeat"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Connecting circuit",
      componentType: "PCM loop",
    });
  },
});
