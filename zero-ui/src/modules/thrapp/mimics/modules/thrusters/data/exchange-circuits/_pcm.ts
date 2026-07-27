import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../dhw/data/shared";

export default toInstance<MimicComponentType.HotWaterCircuit>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("thrusters", { technicalName: "thrusters-pcm-loop" }),
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
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "PCM",
      componentType: "Exchange circuit",
    });
  },
});
