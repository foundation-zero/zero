import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { DC_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toHeatExchanger } from "../../helpers";

export const DC_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1006": toHeatExchanger({
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Top,
      },
      source: getField(SensorComponentType.HeatTransferDevice, "dc", "dcSeawaterExchanger"),
    }),
    "1008": toHeatExchanger({
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Side,
        exchangeCircuit:
          DC_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].domesticHotWater.source,
      },
      source: getField(SensorComponentType.HeatTransferDevice, "dc", "dcDhwExchanger"),
    }),
  },
});
