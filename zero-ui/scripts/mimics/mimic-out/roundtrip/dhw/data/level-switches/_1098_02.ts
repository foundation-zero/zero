import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.LevelSwitch>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.LevelSwitch, "dhw", "dhwLevelSwitchTank2"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Level switch",
      componentType: "Level switch",
    });
  },
});
