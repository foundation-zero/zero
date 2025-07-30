import {
  BlindsControl,
  ControlType,
  ControlTypeMap,
  Room,
  RoomControl,
  RoomSensor,
  SensorType,
  SensorTypeMap,
} from "../../src/@types";
import { boolToInt } from "../../src/lib/mappers";

export const toBlindsControl = (value: number): BlindsControl => ({
  id: "",
  type: ControlType.BLIND,
  value,
  time: Date.now(),
  meta: { opacity: "blind", group: "" },
  name: "",
});

export const toControl =
  <Type extends ControlType, Value = number>(
    type: Type,
    valFn: (value: Value) => number = Number,
  ) =>
  (value: Value): ControlTypeMap[Type] =>
    ({
      id: "",
      type,
      value: valFn(value),
      time: Date.now(),
      name: "",
    }) as ControlTypeMap[Type];

export const toSensor =
  <Type extends SensorType, Value = number>(type: Type, valFn: (value: Value) => number = Number) =>
  (value: Value): SensorTypeMap[Type] =>
    ({
      id: "",
      type,
      value: valFn(value),
      time: Date.now(),
      name: "",
    }) as SensorTypeMap[Type];

export const toLightingControl = toControl(ControlType.LIGHT);
export const toTemperatureControl = toControl(ControlType.TEMPERATURE);
export const toHumidityControl = toControl(ControlType.HUMIDITY);
export const toCO2Control = toControl(ControlType.CO2);
export const toAmplifierStatus = toControl(ControlType.AMPLIFIER, boolToInt);

export const toPresenceSensor = toSensor(SensorType.PRESENCE);
export const toTemperatureSensor = toSensor(SensorType.TEMPERATURE);
export const toHumiditySensor = toSensor(SensorType.HUMIDITY);
export const toCO2Sensor = toSensor(SensorType.CO2);

export const isSensorType =
  <T extends SensorType>(type: T) =>
  (sensor: RoomSensor): sensor is SensorTypeMap[T] =>
    sensor.type === type;

export const isControlType =
  <T extends ControlType>(type: T) =>
  (control: RoomControl): control is ControlTypeMap[T] =>
    control.type === type;

export const isLightControl = isControlType(ControlType.LIGHT);
export const isBlindsControl = isControlType(ControlType.BLIND);
export const isTemperatureControl = isControlType(ControlType.TEMPERATURE);
export const isHumidityControl = isControlType(ControlType.HUMIDITY);
export const isCO2Control = isControlType(ControlType.CO2);
export const isAmplifierControl = isControlType(ControlType.AMPLIFIER);

export const isPresenceSensor = isSensorType(SensorType.PRESENCE);
export const isTemperatureSensor = isSensorType(SensorType.TEMPERATURE);
export const isHumiditySensor = isSensorType(SensorType.HUMIDITY);
export const isCO2Sensor = isSensorType(SensorType.CO2);

export const extractActualSensorValue =
  <T extends SensorType>(type: T) =>
  (room: Room) =>
    room.roomsSensors.find(isSensorType(type))?.value;

export const extractActualControlValue =
  <T extends ControlType>(type: T) =>
  (room: Room) =>
    room.roomsControls.find(isControlType(type))?.value;

export const extractActualHumidity = extractActualSensorValue(SensorType.HUMIDITY);
export const extractActualTemperature = extractActualSensorValue(SensorType.TEMPERATURE);
export const extractActualCO2 = extractActualSensorValue(SensorType.CO2);
export const extractActualPresence = extractActualSensorValue(SensorType.PRESENCE);

export const extractTemperatureSetpoint = extractActualControlValue(ControlType.TEMPERATURE);
export const extractAmplifierStatus = extractActualControlValue(ControlType.AMPLIFIER);
export const extractHumiditySetpoint = extractActualControlValue(ControlType.HUMIDITY);
export const extractCO2Setpoint = extractActualControlValue(ControlType.CO2);
