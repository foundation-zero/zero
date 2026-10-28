import {
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

export default toFlowSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
  },
  source: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
  },
});
