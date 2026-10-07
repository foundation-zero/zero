import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { DRIVES_EXCHANGE_CIRCUIT_DATA } from "../exchange-circuits";

const heatExchanger = (
  field: "drivesDhwExchanger" | "drivesSeawaterExchanger",
  sideA: HeatExchangerPortOrientation,
  sideB: HeatExchangerPortOrientation,
  exchangeCircuit?: ModuleField<SensorComponentType.HeatTransferDevice>,
) => {
  const source = getField(SensorComponentType.HeatTransferDevice, "drives", field);
  return toInstance<MimicComponentType.HeatExchanger>({
    controls: {},
    controllerState: {},
    custom: {
      sideA,
      sideB,
      exchangeCircuit: exchangeCircuit,
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

export const DRIVES_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1011": heatExchanger(
      "drivesSeawaterExchanger",
      HeatExchangerPortOrientation.Side,
      HeatExchangerPortOrientation.Top,
    ),
    "1009": heatExchanger(
      "drivesDhwExchanger",
      HeatExchangerPortOrientation.Top,
      HeatExchangerPortOrientation.Top,
      DRIVES_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].domesticHotWater.source,
    ),
  },
});
