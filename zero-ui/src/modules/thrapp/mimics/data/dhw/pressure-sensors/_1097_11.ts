import { SensorComponentType } from "@/modules/thrsim/types";
import { toPressureSensor } from "../../helpers";

import { getField } from "../../../providers";

export default toPressureSensor({
  source: getField(SensorComponentType.Pressure, "dhw", "dhwPressure"),
});
