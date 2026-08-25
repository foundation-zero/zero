import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { DHW_EXCHANGE_CIRCUIT_DATA } from "..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
export default toInstance<MimicComponentType.HeatExchanger>({
  custom: {
    get exchangeCircuit() {
      return DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].highTempLoop.sensors;
    },
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwConsumersExchanger"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Heat Exchanger",
      componentType: "Heat Exchanger",
    });
  },
});
