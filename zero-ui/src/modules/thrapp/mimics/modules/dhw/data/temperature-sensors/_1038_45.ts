import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank1"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
