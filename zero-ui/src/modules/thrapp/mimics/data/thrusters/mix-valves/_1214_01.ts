import {
  ControlComponentType,
  ControllerStateComponentType,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toMixValve } from "../../helpers";

export default toMixValve(
  {
    controls: {
      valve: getField(ControlComponentType.Valve, "thrusters", "thrustersMixExchanger"),
    },
    controllerState: {
      controller: getField(
        ControllerStateComponentType.PIDController,
        "thrusters",
        "thrustersHeatDumpController",
      ),
    },
    source: getField(SensorComponentType.Valve, "thrusters", "thrustersMixExchanger"),
  },
  { componentType: "Mix valve" },
);
