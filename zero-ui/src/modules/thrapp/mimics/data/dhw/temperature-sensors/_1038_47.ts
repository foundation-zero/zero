import { SensorComponentType } from "@/modules/thrsim/types";
import { toTemperatureSensor } from "../../helpers";

import { getField } from "../../../providers";

export default toTemperatureSensor(
  { source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply") },
  { componentType: "Temperature sensor Pt100 RTD" },
);
