import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "Drives & shore",
    modeModule: "drives",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "drives", "drivesDhwExchanger"),
});
