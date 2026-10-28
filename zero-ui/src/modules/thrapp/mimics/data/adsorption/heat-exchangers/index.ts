import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { ADSORPTION_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toHeatExchanger } from "../../helpers";

export const ADSORPTION_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1003": toHeatExchanger({
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Side,
        exchangeCircuit:
          ADSORPTION_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].highTemperature
            .source,
      },
      source: getField(
        SensorComponentType.HeatTransferDevice,
        "adsorption",
        "adsorptionHtExchanger",
      ),
    }),
    "1004": toHeatExchanger({
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Side,
        exchangeCircuit:
          ADSORPTION_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].domesticHotWater
            .source,
      },
      source: getField(
        SensorComponentType.HeatTransferDevice,
        "adsorption",
        "adsorptionDhwExchanger",
      ),
    }),
    "1005": toHeatExchanger({
      custom: {
        sideA: HeatExchangerPortOrientation.Side,
        sideB: HeatExchangerPortOrientation.Top,
      },
      source: getField(
        SensorComponentType.HeatTransferDevice,
        "adsorption",
        "adsorptionSeawaterExchanger",
      ),
    }),
  },
});
