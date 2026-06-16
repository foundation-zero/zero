import { SensorComponentType } from "@/modules/thrs/types";

import { circuit, exchangeCircuit, toHeatExchanger, tooltip } from ".";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";

export default toHeatExchanger({
  controls: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Side,
    circuit,
    exchangeCircuit,
  },
  parameters: {},
  sensors: {
    heatExchanger: getField(
      SensorComponentType.HeatExchanger,
      "boilers",
      "boilersFahrenheitExchanger",
    ),
  },
  tooltip: tooltip({
    yardTag: "1007",
    technicalName: "Fahrenheit-HotWater-Exchanger",
  }),
});
