import { SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";

const deltaProxy = (field: string) =>
  [SensorComponentType.DeltaT, "thrusters", field] as ModuleField<
    SensorComponentType.DeltaT,
    "thrusters"
  >;

export const THRUSTERS_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ExchangeCircuit]: {
    seawater: toInstance<MimicComponentType.ExchangeCircuit>({
      controls: {},
      controllerState: {},
      custom: {
        circuitName: "Seawater",
        width: 194,
        height: 188,
        forceHeight: true,
      },
      parameters: {},
      source: undefined,
      sensors: {
        deltaT: deltaProxy("thrustersTemperatureSupply"),
        flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
        incoming: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureRecoveryMix",
        ),
        outgoing: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureSupply",
        ),
        heatExchanger: [
          SensorComponentType.HeatExchanger,
          "thrusters",
          "thrustersMixRecovery",
        ] as unknown as ModuleField<SensorComponentType.HeatExchanger, "thrusters">,
      },
      tooltip: {
        title: "Seawater",
        itemName: "Seawater loop",
        technicalName: "thrusters-seawater-loop",
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
          "thrusters",
          "thrustersFlowAft",
        ] as unknown as ModuleField<SensorComponentType.CalculatedFlow, "thrusters">,
        flowOut: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowRecovery"),
        tIn: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureRecoveryMix",
        ),
        tOut: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
      },
      tooltip: {
        title: "PCM",
        itemName: "PCM loop",
        technicalName: "thrusters-pcm-loop",
      },
    }),
  },
});
