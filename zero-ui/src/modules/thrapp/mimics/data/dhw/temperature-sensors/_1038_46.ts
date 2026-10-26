import { SensorComponentType } from "@/modules/thrsim/types";
import { toTemperatureSensor } from "../../helpers";

import { getField } from "../../../providers";
import { drivesFlowController } from "../controllers";

export default toTemperatureSensor(
  {
    custom: { controller: drivesFlowController },
    source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDrivesReturn"),
    sensors: {
      actuator: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
    },
  },
  { componentType: "Temperature sensor Pt100 RTD" },
);
