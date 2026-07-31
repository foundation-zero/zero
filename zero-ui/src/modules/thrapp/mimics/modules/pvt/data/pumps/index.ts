import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import {} from "../controllers";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Pump",
    componentType: "Circulation pump",
  });
export const PVT_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1018": toInstance<MimicComponentType.Pump>({
      custom: {},
      source: getField(SensorComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      controllerState: {},
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      sensors: {
        pressure: getField(SensorComponentType.Pressure, "pvt", "pvtPressureSystem"),
        // flowMeasurement: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
        // temperatureMeasurement: getField(
        //   SensorComponentType.Temperature,
        //   "pvt",
        //   "pvtTemperatureSupply",
        // ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1019": toInstance<MimicComponentType.Pump>({
      custom: {},
      source: getField(SensorComponentType.Pump, "pvt", "pvtPumpMainAft"),
      controllerState: {},
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainAftMinimumPumpDutypoint"),
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      sensors: {
        pressure: getField(SensorComponentType.Pressure, "pvt", "pvtPressureSystem"),
        // flowMeasurement: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
        // temperatureMeasurement: getField(
        //   SensorComponentType.Temperature,
        //   "pvt",
        //   "pvtTemperatureSupply",
        // ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1020": toInstance<MimicComponentType.Pump>({
      custom: {},
      source: getField(SensorComponentType.Pump, "pvt", "pvtPumpOwners"),
      controllerState: {},
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "ownersMinimumPumpDutypoint"),
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      sensors: {
        pressure: getField(SensorComponentType.Pressure, "pvt", "pvtPressureSystem"),
        // flowMeasurement: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
        // temperatureMeasurement: getField(
        //   SensorComponentType.Temperature,
        //   "pvt",
        //   "pvtTemperatureSupply",
        // ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
  },
  [MimicComponentType.ManualPump]: {
    "1182": toInstance<MimicComponentType.ManualPump>({
      custom: {},
      source: getCustomField("pvt", { yardTag: "1182", technicalName: "pvt-pump-bypass-a" }),
      controllerState: {},
      controls: {},
      parameters: {},
      sensors: {},
      get tooltip() {
        return tooltip(this.source);
      },
    }),
  },
});
