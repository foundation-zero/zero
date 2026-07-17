import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersSwitchRecovery"),
  },
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersSwitchRecovery"),
  sensors: {},
  tooltip: tooltip("1066-03", "thrusters-switch-recovery"),
});
