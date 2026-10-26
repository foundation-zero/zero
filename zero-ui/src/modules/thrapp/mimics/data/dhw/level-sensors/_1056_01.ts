import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toInstance } from "../../../modules";

import { getField } from "../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.LevelSensor>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getField(SensorComponentType.Level, "dhw", "dhwLevelTank1"),
  get tooltip() {
    return tooltip(this.source);
  },
});
