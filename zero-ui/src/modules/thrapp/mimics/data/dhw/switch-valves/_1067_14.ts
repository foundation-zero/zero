import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toSwitchValve } from "../../helpers";

import { getField } from "../../../providers";
import { tank1 } from "./shared";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply"),
  },
  custom: tank1,
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply"),
});
