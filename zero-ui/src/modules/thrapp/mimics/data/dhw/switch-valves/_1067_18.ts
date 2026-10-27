import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toSwitchValve } from "../../helpers";

import { getField } from "../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
  },
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
});
