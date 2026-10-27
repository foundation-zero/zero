import {
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toPressureSensor } from "../../helpers";

export const PVT_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-03": toPressureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureMainFwd"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      },
    }),
    "1097-04": toPressureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainAftMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureMainAft"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
      },
    }),
    "1097-05": toPressureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "ownersMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureOwners"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
      },
    }),
    "1097-06": toPressureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureSystem"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      },
    }),
  },
});
