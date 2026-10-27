import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "High temperature",
    modeModule: "pcm",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "consumers", "consumersDhwExchanger"),
});
