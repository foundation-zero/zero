import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { DHW_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
    get exchangeCircuit() {
      return DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].highTempLoop.sensors;
    },
  },
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwConsumersExchanger"),
  sensors: {
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting"),
  },
  tooltip: tooltip({
    yardTag: "1007",
    technicalName: "dhw-consumers-exchanger",
  }),
});
