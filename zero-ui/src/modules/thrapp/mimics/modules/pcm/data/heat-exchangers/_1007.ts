import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField } from "../../../../providers";
import { PCM_EXCHANGE_CIRCUIT_DATA } from "../exchange-circuits";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatExchanger>({
  controls: {},
  controllerState: {},
  custom: {
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
    get exchangeCircuit() {
      return PCM_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].dhw.sensors;
    },
  },
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "consumers", "consumersDhwExchanger"),
  sensors: {
    incoming: getField(
      SensorComponentType.Temperature,
      "consumers",
      "consumersTemperatureDhwSupply",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "consumers",
      "consumersTemperatureDhwReturn",
    ),
    flow: getField(SensorComponentType.Flow, "consumers", "consumersFlowDhw"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
