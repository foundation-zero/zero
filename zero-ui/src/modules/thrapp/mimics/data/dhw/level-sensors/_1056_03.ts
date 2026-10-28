import { getField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "../../../../types";
import { toInstance } from "../../../modules";

import { SensorComponentType } from "@/modules/thrapp/types/thrs";
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
