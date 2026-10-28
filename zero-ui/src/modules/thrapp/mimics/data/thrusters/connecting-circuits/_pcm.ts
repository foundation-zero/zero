import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toConnectingCircuit } from "../../helpers";

export default toConnectingCircuit(
  {
    custom: { circuitName: "PCM", modeModule: "pcm" },
    source: getField(SensorComponentType.HeatTransferDevice, "thrusters", "thrustersPcmHeat"),
  },
  { componentType: "PCM loop" },
);
