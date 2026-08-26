import { getField } from "@/modules/thrapp/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { SensorComponentType } from "@/modules/thrsim/types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
  sensors: {
    actuator: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
