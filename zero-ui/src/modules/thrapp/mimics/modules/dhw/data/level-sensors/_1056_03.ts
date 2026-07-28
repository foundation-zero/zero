import { getField } from "@/modules/thrapp/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { SensorComponentType } from "@/modules/thrsim/types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.LevelSensor>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getField(SensorComponentType.Level, "dhw", "dhwLevelTank3"),
  get tooltip() {
    return tooltip(this.source);
  },
});
