import {
  ControlComponentType,
  ControllerStateComponentType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.MixValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "thrusters", "thrustersMixExchanger"),
  },
  controllerState: {
    controller: getField(
      ControllerStateComponentType.PIDController,
      "thrusters",
      "heatDumpController",
    ),
  },
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "thrusters", "thrustersMixExchanger"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
