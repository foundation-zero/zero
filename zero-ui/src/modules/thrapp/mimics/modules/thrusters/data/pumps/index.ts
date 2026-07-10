import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";

const tooltip = (yardTag: string, technicalName: string, itemName: string) => ({
  title: "Pump",
  itemName,
  yardTag,
  technicalName,
});

export const THRUSTERS_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1194": toInstance<MimicComponentType.Pump>({
      custom: {},
      source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump1"),
      controllerState: {
        flowController: thrustersPidController("pump1FlowController"),
        temperatureController: thrustersPidController("pump1TemperatureController"),
      },
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
      },
      parameters: {
        flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
        temperature: getField(ParametersType.Temperature, "thrusters", "recoveryTemperature"),
      },
      sensors: {
        pressure: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureDischarge"),
        flowMeasurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
        temperatureMeasurement: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureAft",
        ),
      },
      tooltip: tooltip("1194", "thrusters-pump-1", "Thrusters circulation pump AFT"),
    }),
    "1195": toInstance<MimicComponentType.Pump>({
      custom: {},
      source: getField(SensorComponentType.Pump, "thrusters", "thrustersPump2"),
      controllerState: {
        flowController: thrustersPidController("pump2FlowController"),
        temperatureController: thrustersPidController("pump2TemperatureController"),
      },
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
      },
      parameters: {
        flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
        temperature: getField(ParametersType.Temperature, "thrusters", "maximumSupplyTemperature"),
      },
      sensors: {
        pressure: getField(SensorComponentType.Pressure, "thrusters", "thrustersPressureSystem"),
        flowMeasurement: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
        temperatureMeasurement: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureFwd",
        ),
      },
      tooltip: tooltip("1195", "thrusters-pump-2", "Thrusters circulation pump FWD"),
    }),
  },
});
