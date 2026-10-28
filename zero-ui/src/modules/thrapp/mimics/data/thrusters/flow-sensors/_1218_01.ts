import {
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";

export default toFlowSensor({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
  },
  source: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowRecovery"),
  sensors: {
    temperature: getField(
      SensorComponentType.Temperature,
      "thrusters",
      "thrustersTemperatureRecoveryMix",
    ),
  },
});
