import { ControlComponentType, ControllerStateComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.MixValve>({
  custom: {},
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersMixExchanger"),
  },
  controllerState: {
    controller: getField(ControllerStateComponentType.PIDController, "thrusters", "thrustersHeatDumpController"),
  },
  parameters: {},
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersMixExchanger"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Mix valve",
      componentType: "Mix valve",
    });
  },
});
