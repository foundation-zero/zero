import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PVT_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.SeawaterCircuit]: {
    seawater: toInstance<MimicComponentType.SeawaterCircuit>({
      controls: {},
      controllerState: {},
      custom: {
        circuitName: "Seawater",
      },
      parameters: {},
      source: getField(SensorComponentType.Temperature, "pvt", "placeholder"),
      sensors: {},
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Seawater circuit",
          componentType: "Seawater loop",
        });
      },
    }),
  },
  [MimicComponentType.ConnectingCircuit]: {
    pcm: toInstance<MimicComponentType.ConnectingCircuit>({
      controls: {},
      controllerState: {},
      custom: {
        circuitName: "PCM",
        modeModule: "pcm",
      },
      parameters: {},
      source: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPcmHeat"),
      sensors: {},
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Connecting circuit",
          componentType: "PCM loop",
        });
      },
    }),
  },
});
