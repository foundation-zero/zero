import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.PressureSensor>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  sensors: {},
  source: getField(SensorComponentType.Pressure, "dhw", "dhwPressure"),
  get tooltip() {
    return tooltip(this.source);
  },
});
