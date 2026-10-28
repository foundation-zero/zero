import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toTemperatureSensor } from "../../helpers";

import { getField } from "../../../providers";

export default toTemperatureSensor(
  { source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply") },
  { componentType: "Temperature sensor Pt100 RTD" },
);
