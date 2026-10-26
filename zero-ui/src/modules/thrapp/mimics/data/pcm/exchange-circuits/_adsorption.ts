import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toExchangeCircuit } from "../../helpers";

export default toExchangeCircuit({
  custom: {
    circuitName: "Adsorption circuit",
    modeModule: "adsorption",
  },
  source: getField(SensorComponentType.HeatTransferDevice, "adsorption", "adsorptionHtExchanger"),
});
