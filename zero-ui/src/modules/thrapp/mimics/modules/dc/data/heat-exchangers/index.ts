import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { DC_EXCHANGE_CIRCUIT_DATA } from "..";
import { toFieldsMap, toInstance } from "../../..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const heatExchanger = (
  source: ModuleField<SensorComponentType.HeatTransferDevice, "dc">,
  exchangeCircuit?: ModuleField<SensorComponentType.HeatTransferDevice>,
  custom: Partial<{
    sideA: HeatExchangerPortOrientation;
    sideB: HeatExchangerPortOrientation;
  }> = {},
) => {
  return toInstance<MimicComponentType.HeatExchanger>({
    controls: {},
    controllerState: {},
    custom: {
      sideA: HeatExchangerPortOrientation.Side,
      sideB: HeatExchangerPortOrientation.Top,
      exchangeCircuit: exchangeCircuit,
      ...custom,
    },
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Heat exchanger",
        componentType: "Heat exchanger",
      });
    },
  });
};

export const DC_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1006": heatExchanger(
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcSeawaterExchanger"),
    ),
    "1008": heatExchanger(
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcDhwExchanger"),
      DC_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].domesticHotWater.source,

      {
        sideB: HeatExchangerPortOrientation.Side,
      },
    ),
  },
});
