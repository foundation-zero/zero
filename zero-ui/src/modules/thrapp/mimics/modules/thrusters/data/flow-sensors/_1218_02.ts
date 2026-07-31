import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  controllerState: {},
  custom: {},
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
  },
  source: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
