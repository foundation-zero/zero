import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { dcFlowController } from "../controllers";
export default toInstance<MimicComponentType.TemperatureSensor>({
  custom: {
    controller: dcFlowController,
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDcReturn"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Temperature sensor",
      componentType: "Temperature sensor Pt100 RTD",
    });
  },
});
