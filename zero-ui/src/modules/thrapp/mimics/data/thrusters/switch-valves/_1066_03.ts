import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toSwitchValve } from "../../helpers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersSwitchRecovery"),
  },
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersSwitchRecovery"),
});
