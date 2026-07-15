import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { controllerState, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState,
  custom: {
    actuator: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  },
  parameters,
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureDcReturn"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1038-26",
    technicalName: "dhw-temperature-dc-return",
  }),
});
