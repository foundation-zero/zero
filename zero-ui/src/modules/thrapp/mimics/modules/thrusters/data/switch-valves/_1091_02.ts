import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersSwitchFwd"),
  },
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersSwitchFwd"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
