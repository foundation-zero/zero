import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Pressure sensor",
  itemName: "Pressure sensor",
  yardTag,
  technicalName,
});

export const THRUSTERS_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-01": toInstance<MimicComponentType.PressureSensor>({
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
      tooltip: tooltip("1097-01", "thrusters-pressure-discharge"),
    }),
    "1097-02": toInstance<MimicComponentType.PressureSensor>({
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
    }),
  },
});
