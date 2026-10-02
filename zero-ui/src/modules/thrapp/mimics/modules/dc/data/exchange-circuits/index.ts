import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const exchangeCircuit = (
  circuitName: string,
  source: ModuleField<SensorComponentType.HeatTransferDevice>,
) =>
  toInstance<MimicComponentType.ExchangeCircuit>({
    controls: {},
    controllerState: {},
    custom: { circuitName },
    parameters: {},
    sensors: {},
    source,
    get tooltip(): TooltipContent {
      return fieldTooltip(this.source, {
        title: "Exchange circuit",
        componentType: `${circuitName} loop`,
      });
    },
  });

export const DC_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ExchangeCircuit]: {
    seawater: exchangeCircuit(
      "Seawater",
      getField(SensorComponentType.HeatTransferDevice, "dc", "placeholder"),
    ),
    domesticHotWater: exchangeCircuit(
      "Domestic Hot Water",
      getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwDcExchanger"),
    ),
  },
});
