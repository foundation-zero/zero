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
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1038-25",
    technicalName: "dhw-temperature-hvac-exchanger-return",
  }),
});
