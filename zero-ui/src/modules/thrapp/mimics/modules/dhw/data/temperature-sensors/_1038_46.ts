import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { drivesFlowController } from "../controllers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState: {},
  custom: { controller: drivesFlowController },
  parameters: {},
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDrivesReturn"),
  sensors: {
    actuator: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDrives"),
  },
  tooltip: tooltip({
    yardTag: "1038-46",
    technicalName: "dhw-temperature-drives-return",
  }),
});
