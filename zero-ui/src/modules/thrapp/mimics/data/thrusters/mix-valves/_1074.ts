import {
  ControlComponentType,
  ControllerStateComponentType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toMixValve } from "../../helpers";

export default toMixValve(
  {
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
    source: getField(SensorComponentType.Valve, "thrusters", "thrustersMixRecovery"),
  },
  { componentType: "Mix valve" },
);
