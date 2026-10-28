import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toInstance } from "../../../modules";
import { getField } from "../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ThreeWaySwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersSwitchAft"),
  },
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersSwitchAft"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
