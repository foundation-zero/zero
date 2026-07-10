import { SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";

const deltaProxy = (field: string) =>
  [SensorComponentType.DeltaT, "pvt", field] as ModuleField<SensorComponentType.DeltaT, "pvt">;

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
      source: undefined,
      sensors: {
        deltaT: deltaProxy("pvtTemperatureSupply"),
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
        incoming: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
        outgoing: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
        heatExchanger: [
          SensorComponentType.HeatExchanger,
          "pvt",
          "pvtMixExchanger",
        ] as unknown as ModuleField<SensorComponentType.HeatExchanger, "pvt">,
      },
      tooltip: {
        title: "Seawater",
        itemName: "Seawater loop",
        technicalName: "pvt-seawater-loop",
      },
    }),
  },
  [MimicComponentType.HotWaterCircuit]: {
    pcm: toInstance<MimicComponentType.HotWaterCircuit>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      source: undefined,
      sensors: {
        flowIn: [
          SensorComponentType.CalculatedFlow,
          "pvt",
          "pvtFlowMainAftRecovery",
        ] as unknown as ModuleField<SensorComponentType.CalculatedFlow, "pvt">,
        flowOut: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
        tIn: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
        tOut: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
      },
      tooltip: {
        title: "PCM",
        itemName: "PCM loop",
        technicalName: "pvt-pcm-loop",
      },
    }),
  },
});
