import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Temperature sensor",
  itemName: "Temperature sensor",
  yardTag,
  technicalName,
});

export const THRUSTERS_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-01": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
      },
      controllerState: {
        controller: thrustersPidController("aftTemperatureController"),
      },
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "thrusters", "warmupTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureAft"),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureAft",
        ),
      },
      tooltip: tooltip("1038-01", "thrusters-temperature-aft"),
    }),
    "1038-02": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
      },
      controllerState: {
        controller: thrustersPidController("fwdTemperatureController"),
      },
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "thrusters", "coolingTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureFwd"),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureFwd",
        ),
      },
      tooltip: tooltip("1038-02", "thrusters-temperature-fwd"),
    }),
    "1038-28": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
      },
      controllerState: {
        controller: thrustersPidController("supplyTemperatureController"),
      },
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "thrusters", "maximumSupplyTemperature"),
      },
      source: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureSupply",
        ),
      },
      tooltip: tooltip("1038-28", "thrusters-temperature-supply"),
    }),
    "1038-30": toInstance<MimicComponentType.TemperatureSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
      },
      controllerState: {
        controller: thrustersPidController("recoveryTemperatureController"),
      },
      custom: {},
      parameters: {
        temperature: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
      },
      source: getField(
        SensorComponentType.Temperature,
        "thrusters",
        "thrustersTemperatureRecoveryMix",
      ),
      sensors: {
        measurement: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureRecoveryMix",
        ),
      },
      tooltip: tooltip("1038-30", "thrusters-temperature-recovery-mix"),
    }),
  },
});
