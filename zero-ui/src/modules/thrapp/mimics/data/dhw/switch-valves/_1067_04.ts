import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toSwitchValve } from "../../helpers";

import { getField } from "../../../providers";
import { tank3 } from "./shared";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank3BoostingReturn"),
  },
  custom: tank3,
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingReturn"),
});
