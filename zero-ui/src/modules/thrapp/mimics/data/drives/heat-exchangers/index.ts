import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toHeatExchanger } from "../../helpers";
import { DRIVES_EXCHANGE_CIRCUIT_DATA } from "../exchange-circuits";

export const DRIVES_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1011": toHeatExchanger({
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Top,
      },
      source: getField(SensorComponentType.HeatTransferDevice, "drives", "drivesSeawaterExchanger"),
    }),
    "1009": toHeatExchanger({
      custom: {
        sideA: HeatExchangerPortOrientation.Top,
        sideB: HeatExchangerPortOrientation.Top,
        exchangeCircuit:
          DRIVES_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].domesticHotWater.source,
      },
      source: getField(SensorComponentType.HeatTransferDevice, "drives", "drivesDhwExchanger"),
    }),
  },
});
