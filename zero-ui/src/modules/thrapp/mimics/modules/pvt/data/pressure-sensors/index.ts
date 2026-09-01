import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Pressure sensor",
    componentType: "Pressure sensor",
  });

export const PVT_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-03": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureMainFwd"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1097-04": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainAftMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureMainAft"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1097-05": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "ownersMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureOwners"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1097-06": toInstance<MimicComponentType.PressureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Pressure, "pvt", "pvtPressureSystem"),
      sensors: {
        flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
  },
});
