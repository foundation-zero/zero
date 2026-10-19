import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toConnectingCircuit } from "../../helpers";

export default toConnectingCircuit(
  {
    custom: { circuitName: "PCM", modeModule: "pcm" },
    source: getField(SensorComponentType.HeatTransferDevice, "thrusters", "thrustersPcmHeat"),
  },
  { componentType: "PCM loop" },
);
