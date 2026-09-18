import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.ConnectingCircuit>({
  controls: {},
  controllerState: {},
  custom: { modeModule: "thrusters" },
  parameters: {},
  source: getCustomField("thrusters", { technicalName: "pcm-thrusters-loop" }),
  sensors: {
    flowIn: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowRecovery"),
    flowOut: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowRecovery"),
    tOut: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureProducersSupply"),
    tIn: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Thrusters",
      componentType: "Thruster loop",
    });
  },
});
