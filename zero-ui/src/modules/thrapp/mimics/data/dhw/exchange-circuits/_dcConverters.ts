import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "DC Converters",
    modeModule: "dc",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "dc", "dcDhwExchanger"),
});
