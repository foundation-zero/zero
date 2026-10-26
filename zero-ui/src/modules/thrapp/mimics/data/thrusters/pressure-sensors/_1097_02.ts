import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toPressureSensor } from "../../helpers";

import { getField } from "../../../providers";

export default toPressureSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
  },
  source: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureSystem"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
  },
});
