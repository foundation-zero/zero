import { getField } from "@/modules/thrapp/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { SensorComponentType } from "@/modules/thrs/types";
import { controllerState, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.TemperatureSensor>({
  controls: {},
  controllerState,
  custom: {},
  parameters,
  source: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
  sensors: {
    actuator: getField(SensorComponentType.Valve, "dhw", "dhwSwitchHighTemperature"),
  },
  tooltip: tooltip({
    yardTag: "1038-65",
    technicalName: "dhw-temperature-boosting-supply",
  }),
});
