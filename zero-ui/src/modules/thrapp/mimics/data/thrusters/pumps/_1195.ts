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
    source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump2"),
    controls: {
      pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
    },
    parameters: {
      flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
      temperature: getField(ParametersType.Temperature, "thrusters", "maximumSupplyTemperature"),
    },
  },
  { componentType: "Thrusters circulation pump FWD" },
);
