import { SensorComponentType } from "@/modules/thrs/types";
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
    get exchangeCircuit() {
      return DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].adsorption.sensors;
    },
  },
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwAdsorptionExchanger"),
  parameters: {},
  sensors: {
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureAdsorptionReturn"),
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowDc"),
  },
  tooltip: tooltip({
    yardTag: "1004",
    technicalName: "adsorption-hot-water-exchanger",
  }),
});
