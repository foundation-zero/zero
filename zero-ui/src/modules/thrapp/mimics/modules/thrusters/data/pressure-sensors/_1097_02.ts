import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.PressureSensor>({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  controllerState: {
    controller: thrustersPidController("systemPressureController"),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
  },
  source: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureSystem"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
  },
  tooltip: tooltip("1097-02", "thrusters-pressure-system"),
});
