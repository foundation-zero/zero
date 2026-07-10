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

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Temperature sensor",
  itemName: "Temperature sensor",
  yardTag,
  technicalName,
});

export const PVT_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-03": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {
        controller: pid("pvtMainFwdTemperatureController"),
      },
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
      tooltip: tooltip("1038-03", "pvt-temperature-main-fwd-return"),
    }),
    "1038-73": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {
        controller: pid("pvtMainAftTemperatureController"),
      },
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
      tooltip: tooltip("1038-73", "pvt-temperature-main-aft-return"),
    }),
    "1038-04": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {
        controller: pid("pvtOwnersTemperatureController"),
      },
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "minimumReturnTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      },
      tooltip: tooltip("1038-04", "pvt-temperature-owners-return"),
    }),
    "1038-22": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {
        controller: pid("pvtMainAftSupplyTemperatureController"),
      },
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
      tooltip: tooltip("1038-22", "pvt-temperature-main-aft-supply"),
    }),
    "1038-21": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {
        controller: pid("pvtOwnersSupplyTemperatureController"),
      },
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersSupply"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersSupply"),
      },
      tooltip: tooltip("1038-21", "pvt-temperature-owners-supply"),
    }),
    "1038-24": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {
        controller: pid("pvtSupplyTemperatureController"),
      },
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "maximumSupplyTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
      },
      tooltip: tooltip("1038-24", "pvt-temperature-supply"),
    }),
  },
});
