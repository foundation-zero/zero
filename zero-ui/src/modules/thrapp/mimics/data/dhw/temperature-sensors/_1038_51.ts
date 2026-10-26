import { SensorComponentType } from "@/modules/thrsim/types";
import { toTemperatureSensor } from "../../helpers";

import { getField } from "../../../providers";
import { dcFlowController } from "../controllers";

export default toTemperatureSensor(
  {
    custom: {
      controller: dcFlowController,
    },
    source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureAdsorptionReturn"),
    sensors: {
      actuator: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
    },
  },
  { componentType: "Temperature sensor Pt100 RTD" },
);
