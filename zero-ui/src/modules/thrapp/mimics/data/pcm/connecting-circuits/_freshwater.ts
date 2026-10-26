import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toConnectingCircuit } from "../../helpers";

export default toConnectingCircuit(
  {
    custom: { circuitName: "Fresh water" },
    source: getField(SensorComponentType.HeatTransferDevice, "pcm", "pcmFreshwaterHeat"),
  },
  { componentType: "Fresh water loop" },
);
