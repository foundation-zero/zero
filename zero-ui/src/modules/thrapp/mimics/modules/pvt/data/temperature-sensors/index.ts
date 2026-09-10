import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Temperature sensor",
    componentType: "Temperature sensor",
  });

export const PVT_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-03": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "warmupTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainFwdReturn"),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainFwdReturn",
        ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1038-73": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "warmupTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainAftReturn"),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainAftReturn",
        ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1038-04": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "minimumReturnTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1038-23": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainFwdSupply"),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainFwdSupply",
        ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1038-22": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainAftSupply"),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainAftSupply",
        ),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1038-21": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersSupply"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersSupply"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1038-24": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {},
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "maximumSupplyTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
      },
      get tooltip() {
        return tooltip(this.source);
      },
    }),
  },
});
