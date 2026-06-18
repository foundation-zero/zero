import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { BOILER_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
    get circuit() {
      return BOILER_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].fahrenheit.sensors;
    },
    get exchangeCircuit() {
      return BOILER_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].fahrenheit.sensors;
    },
  },
  source: getField(SensorComponentType.HeatExchanger, "boilers", "boilersFahrenheitExchanger"),
  parameters: {},
  sensors: {},
  tooltip: tooltip({
    yardTag: "1004",
    technicalName: "Fahrenheit-HotWater-Exchanger",
  }),
});
