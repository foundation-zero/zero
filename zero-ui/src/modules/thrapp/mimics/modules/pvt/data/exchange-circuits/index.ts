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
        width: 194,
        height: 168,
        forceHeight: true,
      },
      parameters: {},
      source: getCustomField("pvt", { technicalName: "pvt-seawater-loop" }),
      sensors: {
        flow: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtSeawaterExchangerFlow"),
        incoming: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
        outgoing: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
        heatExchanger: getField(SensorComponentType.HeatExchanger, "pvt", "pvtSeawaterExchanger"),
      },
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Seawater",
          componentType: "Seawater loop",
        });
      },
    }),
  },
  [MimicComponentType.HotWaterCircuit]: {
    pcm: toInstance<MimicComponentType.HotWaterCircuit>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      source: getCustomField("pvt", { technicalName: "pvt-pcm-loop" }),
      sensors: {
        flowIn: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtTotalFlow"),
        flowOut: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtTotalFlow"),
        tIn: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
        tOut: getField(SensorComponentType.Temperature, "pvt", "pcmTemperatureProducersSupply"),
      },
      get tooltip() {
        return fieldTooltip(this.source, { title: "PCM", componentType: "PCM loop" });
      },
    }),
  },
});
