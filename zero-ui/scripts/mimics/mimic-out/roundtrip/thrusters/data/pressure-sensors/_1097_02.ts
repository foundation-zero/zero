import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.PressureSensor>({
  custom: {},
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
  },
  controllerState: {},
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
  },
  source: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureSystem"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Pressure sensor",
      componentType: "Pressure sensor",
    });
  },
});
