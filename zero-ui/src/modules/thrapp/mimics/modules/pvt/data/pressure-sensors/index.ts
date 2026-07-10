import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";

const pid = (name: string) =>
  [ControllerStateComponentType.PIDController, "pvt", name] as ModuleField<
    ControllerStateComponentType.PIDController,
    "pvt"
  >;

const flowParam = (name: string) =>
  [ParametersType.Flow, "pvt", name] as ModuleField<ParametersType.Flow, "pvt">;

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Pressure sensor",
  itemName: "Pressure sensor",
  yardTag,
  technicalName,
});

export const PVT_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-03": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {
        controller: pid("pvtMainFwdPressureController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureMainFwd"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      },
      tooltip: tooltip("1097-03", "pvt-pressure-main-fwd"),
    }),
    "1097-04": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {
        controller: pid("pvtMainAftPressureController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("mainAftMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureMainAft"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
      },
      tooltip: tooltip("1097-04", "pvt-pressure-main-aft"),
    }),
    "1097-05": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {
        controller: pid("pvtOwnersPressureController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("ownersMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureOwners"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
      },
      tooltip: tooltip("1097-05", "pvt-pressure-owners"),
    }),
    "1097-06": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {
        controller: pid("pvtSystemPressureController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureSystem"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      },
      tooltip: tooltip("1097-06", "pvt-pressure-system"),
    }),
  },
});
