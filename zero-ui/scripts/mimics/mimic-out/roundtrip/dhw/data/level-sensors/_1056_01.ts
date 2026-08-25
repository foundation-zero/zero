import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.LevelSensor>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Level, "dhw", "dhwLevelTank1"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Tank level sensor",
      componentType: "Tank level sensor",
    });
  },
});
