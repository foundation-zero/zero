import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toConnectingCircuit } from "../../helpers";

export default toConnectingCircuit(
  {
    custom: {
      circuitName: "PVT",
      modeModule: "pvt",
    },
    source: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPcmHeat"),
  },
  { componentType: "PVT loop" },
);
