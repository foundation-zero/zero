import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "High temperature",
    modeModule: "pcm",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "consumers", "consumersDhwExchanger"),
});
