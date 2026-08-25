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
      return DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].brightloop.sensors;
    },
    sideA: HeatExchangerPortOrientation.Side,
    sideB: HeatExchangerPortOrientation.Top,
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDcExchanger"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowDc"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDcReturn"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Heat Exchanger",
      componentType: "Heat Exchanger",
    });
  },
});
