import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { circuit, exchangeCircuit, tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
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
    yardTag: "1004",
    technicalName: "Fahrenheit-HotWater-Exchanger",
  }),
});
