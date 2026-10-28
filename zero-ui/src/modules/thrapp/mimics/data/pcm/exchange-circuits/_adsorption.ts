import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "Adsorption circuit",
    modeModule: "adsorption",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "adsorption", "adsorptionHtExchanger"),
});
