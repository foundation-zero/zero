import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toSwitchValve } from "../../helpers";

import { getField } from "../../../providers";
import { tank2 } from "./shared";

export default toSwitchValve({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank2Outlet"),
  },
  custom: tank2,
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Outlet"),
});
