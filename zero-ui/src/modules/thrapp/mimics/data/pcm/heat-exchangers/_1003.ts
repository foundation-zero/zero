import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toHeatExchanger } from "../../helpers";

import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { getField } from "../../../providers";
import { PCM_EXCHANGE_CIRCUIT_DATA } from "../exchange-circuits";

export default toHeatExchanger(
  {
    custom: {
      sideA: HeatExchangerPortOrientation.Side,
      sideB: HeatExchangerPortOrientation.Top,
      exchangeCircuit:
        PCM_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].adsorption.source,
    },
    source: getField(
      SensorComponentType.HeatTransferDevice,
      "consumers",
      "consumersAdsorptionExchanger",
    ),
  },
  { title: "Heat Exchanger", componentType: "Heat Exchanger" },
);
