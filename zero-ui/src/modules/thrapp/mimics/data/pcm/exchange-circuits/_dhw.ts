import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "Domestic hot water",
    modeModule: "dhw",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwConsumersExchanger"),
});
