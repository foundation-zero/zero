import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank2, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank2BoostingReturn"),
  },
  controllerState: {},
  custom: tank2,
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingReturn"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
