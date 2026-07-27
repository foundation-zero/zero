import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { THRUSTERS_EXCHANGE_CIRCUIT_DATA } from "..";
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
      THRUSTERS_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].seawater.sensors,
  },
  source: getField(SensorComponentType.HeatExchanger, "thrusters", "thrustersSeawaterExchanger"),
  parameters: {},
  sensors: {
    incoming: getField(
      SensorComponentType.Temperature,
      "thrusters",
      "thrustersTemperatureRecoveryMix",
    ),
    outgoing: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowRecovery"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
