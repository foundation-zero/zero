import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { pumpTemperatureController } from "../controllers";
export default toInstance<MimicComponentType.TemperatureSensor>({
  custom: {
    controller: pumpTemperatureController,
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Temperature sensor",
      componentType: "Temperature sensor Pt100 RTD",
    });
  },
});
