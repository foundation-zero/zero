import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toHeatExchanger } from "../../helpers";

import { DHW_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { getField } from "../../../providers";

export default toHeatExchanger(
  {
    custom: {
      sideA: HeatExchangerPortOrientation.Side,
      sideB: HeatExchangerPortOrientation.Top,
      exchangeCircuit:
        DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].adsorption.source,
    },
    source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwAdsorptionExchanger"),
  },
  { title: "Heat Exchanger", componentType: "Heat Exchanger" },
);
