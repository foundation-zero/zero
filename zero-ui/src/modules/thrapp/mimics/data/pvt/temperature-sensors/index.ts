import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";
import { PVT_AFT_TEMPERATURE_SENSORS } from "./_aft";
import { PVT_OWNERS_TEMPERATURE_SENSORS } from "./_owners";

export const PVT_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-03": toTemperatureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
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
    }),
    "1038-73": toTemperatureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
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
    }),
    "1038-04": toTemperatureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "minimumReturnTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      },
    }),
    "1038-23": toTemperatureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
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
    }),
    "1038-22": toTemperatureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
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
    }),
    "1038-21": toTemperatureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersSupply"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersSupply"),
      },
    }),
    "1038-24": toTemperatureSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      parameters: {
        temperature: getField(ParametersType.Temperature, "pvt", "maximumSupplyTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
      sensors: {
        measurement: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureSupply"),
      },
    }),
    ...PVT_AFT_TEMPERATURE_SENSORS,
    ...PVT_OWNERS_TEMPERATURE_SENSORS,
  },
});
