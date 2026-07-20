import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.PressureSensor>({
  controls: {
    pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
  },
  controllerState: {
    controller: thrustersPidController("dischargePressureController"),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
  },
  source: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureDischarge"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
  },
  tooltip: tooltip({
    yardTag: "1097-01",
    technicalName: "thrusters-pressure-discharge",
  }),
});
