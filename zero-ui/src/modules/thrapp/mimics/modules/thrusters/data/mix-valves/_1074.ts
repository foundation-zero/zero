import {
  ControlComponentType,
  ControllerStateComponentType,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.MixValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersMixRecovery"),
  },
  controllerState: {
    controller: getField(
      ControllerStateComponentType.PIDController,
      "thrusters",
      "thrustersWarmupMixController",
    ),
  },
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersMixRecovery"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
