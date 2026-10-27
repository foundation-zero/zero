import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toConnectingCircuit } from "../../helpers";

export default toConnectingCircuit(
  {
    custom: { circuitName: "Fresh water" },
    source: getField(SensorComponentType.HeatTransferDevice, "pcm", "pcmFreshwaterHeat"),
  },
  { componentType: "Fresh water loop" },
);
