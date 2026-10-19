import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toSwitchValve } from "../../helpers";

import { getField } from "../../../providers";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchLowTemperature"),
  },
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchLowTemperature"),
});
