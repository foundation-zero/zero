import {
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { toPressureSensor } from "../../helpers";

import { getField } from "../../../providers";

export default toPressureSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
  },
  source: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureDischarge"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
  },
});
