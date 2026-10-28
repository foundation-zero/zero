import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toSwitchValve } from "../../helpers";

import { getField } from "../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchHeatpump"),
  },
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHeatpump"),
});
