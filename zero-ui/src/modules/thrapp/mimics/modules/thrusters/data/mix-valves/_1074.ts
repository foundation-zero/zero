import {
  ControlComponentType,
  ControllerStateComponentType,
  SensorComponentType,
} from "@/modules/thrs/types";
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
      "warmupMixController",
    ),
  },
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersMixRecovery"),
  sensors: {},
  tooltip: tooltip("1074", "thrusters-mix-recovery"),
});
