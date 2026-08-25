import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.PressureSensor>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Pressure, "dhw", "dhwPressure"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Pressure sensor",
      componentType: "Pressure sensor",
    });
  },
});
