import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "Drives & shore",
    modeModule: "drives",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "drives", "drivesDhwExchanger"),
});
