import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { tooltip } from "./shared";

export const deltaProxy = (field: string) =>
  [SensorComponentType.DeltaT, "thrusters", field] as ModuleField<
    SensorComponentType.DeltaT,
    "thrusters"
  >;

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Seawater",
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
    outgoing: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
    heatExchanger: [
      SensorComponentType.HeatExchanger,
      "thrusters",
      "thrustersMixRecovery",
    ] as unknown as ModuleField<SensorComponentType.HeatExchanger, "thrusters">,
  },
  tooltip: tooltip({
    title: "Seawater",
    technicalName: "thrusters-seawater-loop",
  }),
});
