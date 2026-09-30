import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const heatExchanger = (
  yardTag: string,
  custom: Partial<{
    sideA: HeatExchangerPortOrientation;
    sideB: HeatExchangerPortOrientation;
    exchangeCircuit: ModuleField<SensorComponentType.HeatTransferDevice, "dc">;
  }> = {},
) => {
  const source = getField(SensorComponentType.HeatTransferDevice, "dc", "dcDhwExchanger");

  return toInstance<MimicComponentType.HeatExchanger>({
    controls: {},
    controllerState: {},
    custom: {
      sideA: HeatExchangerPortOrientation.Side,
      sideB: HeatExchangerPortOrientation.Top,
      exchangeCircuit: source,
      ...custom,
    },
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Heat exchanger",
        componentType: "Heat exchanger",
        yardTag,
      });
    },
  });
};

export const DC_HEAT_EXCHANGER_DATA = toFieldsMap({
  [MimicComponentType.HeatExchanger]: {
    "1006": heatExchanger("1006"),
    "1002": heatExchanger("1002", { sideB: HeatExchangerPortOrientation.Side }),
  },
});
