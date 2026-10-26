import { getField } from "@/modules/thrapp/mimics/providers";
import { toTemperatureSensor } from "../../helpers";

import { SensorComponentType } from "@/modules/thrsim/types";

export default toTemperatureSensor(
  {
    source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
    sensors: {
      actuator: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
    },
  },
  { componentType: "Temperature sensor Pt100 RTD" },
);
