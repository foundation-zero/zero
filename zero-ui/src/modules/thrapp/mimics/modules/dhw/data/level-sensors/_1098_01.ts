import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.LevelSensor>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getField(SensorComponentType.Level, "dhw", "dhwLevelTank1"),
  tooltip: tooltip({
    yardTag: "1098-01",
    technicalName: "dhw-level-1098-01",
  }),
});
