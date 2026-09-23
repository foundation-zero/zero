import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PVT_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ExchangeCircuit]: {
    seawater: toInstance<MimicComponentType.ExchangeCircuit>({
      controls: {},
      controllerState: {},
      custom: {
        circuitName: "Seawater",
      },
      parameters: {},
      source: getField(SensorComponentType.HeatTransferDevice, "pvt", "placeholder"),
      sensors: {},
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Exchange circuit",
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
        modeModule: "pcm",
      },
      parameters: {},
      source: getCustomField("pvt", { technicalName: "pvt-pcm-loop" }),
      sensors: {
        flowIn: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtTotalFlow"),
        flowOut: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtTotalFlow"),
        tIn: getField(SensorComponentType.CalculatedTemperature, "pvt", "pvtReturnTemperature"),
        tOut: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureProducersSupply"),
      },
      get tooltip() {
        return fieldTooltip(this.source, { title: "PCM", componentType: "PCM loop" });
      },
    }),
  },
});
