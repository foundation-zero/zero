import { getField } from "@/modules/heat-system/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { SensorComponentType } from "@/modules/heat-system-simulation/types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.LevelSwitch>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getField(SensorComponentType.LevelSwitch, "dhw", "dhwLevelSwitchTank2"),
  get tooltip() {
    return tooltip(this.source);
  },
});
