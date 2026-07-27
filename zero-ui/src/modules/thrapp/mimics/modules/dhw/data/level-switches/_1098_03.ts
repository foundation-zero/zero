import { getField } from "@/modules/thrapp/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { SensorComponentType } from "@/modules/thrs/types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.LevelSwitch>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getField(SensorComponentType.LevelSwitch, "dhw", "dhwLevelSwitchTank3"),
  tooltip: tooltip({
    yardTag: "1098-03",
    technicalName: "dhw-level-switch-tank-3",
  }),
});
