import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toExchangeCircuit, toSeawaterCircuit } from "../../helpers";

export const DRIVES_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.SeawaterCircuit]: {
    seawater: toSeawaterCircuit({
      custom: { circuitName: "Seawater" },
      source: getField(SensorComponentType.Temperature, "dc", "placeholder"),
    }),
  },
  [MimicComponentType.ExchangeCircuit]: {
    domesticHotWater: toExchangeCircuit(
      {
        custom: { circuitName: "Domestic Hot Water", modeModule: "dhw" },
        source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwDrivesExchanger"),
      },
      { componentType: "Domestic Hot Water loop" },
    ),
  },
});
