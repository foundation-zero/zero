import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { dcFlowController } from "../controllers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState: {},
  custom: {
    controller: dcFlowController,
  },
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureAdsorptionReturn"),
  sensors: {
    actuator: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  },
  tooltip: tooltip({
    yardTag: "1038-51",
    technicalName: "dhw-temperature-adsorption-return",
  }),
});
