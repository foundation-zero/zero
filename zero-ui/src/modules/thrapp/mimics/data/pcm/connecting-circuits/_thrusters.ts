import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toConnectingCircuit } from "../../helpers";

export default toConnectingCircuit(
  {
    custom: {
      circuitName: "Thrusters",
      modeModule: "thrusters",
    },
    source: getField(SensorComponentType.HeatTransferDevice, "thrusters", "thrustersPcmHeat"),
  },
  { componentType: "Thrusters loop" },
);
