import {
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { toPump } from "../../helpers";

import { getField } from "../../../providers";
import { pumpController } from "../controllers";

export default toPump(
  {
    custom: {
      controllers: [pumpController],
    },
    source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump1"),
    controls: {
      pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
    },
    parameters: {
      flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
      temperature: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
    },
  },
  { componentType: "Thrusters circulation pump AFT" },
);
