import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { THRUSTERS_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
export default toInstance<MimicComponentType.HeatExchanger>({
  custom: {
    get exchangeCircuit() {
      return THRUSTERS_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].seawater.sensors;
    },
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "thrusters", "thrustersSeawaterExchanger"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowRecovery"),
    incoming: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureRecoveryMix"),
    outgoing: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Heat Exchanger",
      componentType: "Heat Exchanger",
    });
  },
});
