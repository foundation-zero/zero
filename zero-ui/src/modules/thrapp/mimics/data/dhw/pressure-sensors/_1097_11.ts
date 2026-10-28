import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toPressureSensor } from "../../helpers";

import { getField } from "../../../providers";

export default toPressureSensor({
  source: getField(SensorComponentType.Pressure, "dhw", "dhwPressure"),
});
