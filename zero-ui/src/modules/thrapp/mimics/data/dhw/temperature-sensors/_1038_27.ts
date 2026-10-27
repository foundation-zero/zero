import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toTemperatureSensor } from "../../helpers";

import { getField } from "../../../providers";

export default toTemperatureSensor(
  { source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank3") },
  { componentType: "Temperature sensor Pt100 RTD" },
);
