import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { DHW_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  controllerState: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
    exchangeCircuit:
      DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].adsorption.source,
  },
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwAdsorptionExchanger"),
  parameters: {},
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
