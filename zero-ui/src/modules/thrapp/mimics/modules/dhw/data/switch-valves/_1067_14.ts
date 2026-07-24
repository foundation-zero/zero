import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank1, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply"),
  },
  controllerState: {},
  custom: tank1,
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
