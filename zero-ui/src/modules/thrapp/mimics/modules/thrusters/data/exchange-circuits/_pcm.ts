import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HotWaterCircuit>({
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
    tIn: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureRecoveryMix"),
    tOut: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
  },
  tooltip: tooltip({
    title: "PCM",
    technicalName: "thrusters-pcm-loop",
  }),
});
