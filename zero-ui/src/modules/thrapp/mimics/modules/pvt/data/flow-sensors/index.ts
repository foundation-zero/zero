import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow sensor",
    componentType: "Flow sensor",
  });

export const PVT_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1058-12": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainFwdReturn",
        ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1058-13": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainAftMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainAftReturn",
        ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1057-03": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "ownersMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
      sensors: {
        temperature: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
  },
});
