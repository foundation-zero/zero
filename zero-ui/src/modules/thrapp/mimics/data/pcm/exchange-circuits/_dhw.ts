import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "Domestic hot water",
    modeModule: "dhw",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwConsumersExchanger"),
});
