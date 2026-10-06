import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const DRIVES_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.SeawaterCircuit]: {
    seawater: toInstance<MimicComponentType.SeawaterCircuit>({
      controls: {},
      controllerState: {},
      custom: { circuitName: "Seawater" },
      parameters: {},
      sensors: {},
      source: getField(SensorComponentType.Temperature, "dc", "placeholder"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Seawater circuit",
          componentType: `Seawater loop`,
        });
      },
    }),
  },
  [MimicComponentType.ExchangeCircuit]: {
    domesticHotWater: toInstance<MimicComponentType.ExchangeCircuit>({
      controls: {},
      controllerState: {},
      custom: { circuitName: "Domestic Hot Water", modeModule: "dhw" },
      parameters: {},
      sensors: {},
      source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwDrivesExchanger"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Exchange circuit",
          componentType: "Domestic Hot Water loop",
        });
      },
    }),
  },
});
