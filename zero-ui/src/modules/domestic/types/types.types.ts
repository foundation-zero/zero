import { DomesticBlinds, DomesticLightingGroups, DomesticRooms } from "../gql/graphql";
import { RoomGroup, ValidationStatus } from "./types.consts";

export interface ValueWithTime {
  time: Date;
  value: number;
}

export interface Meta<T extends Record<string, unknown>> {
  meta: T;
}

export type BlindsType = "blind" | "shear";

export type BlindsMeta = {
  opacity: BlindsType;
  group: string;
};

export type LightingGroup = {
  id: string;
  name: string;
  level: number;
};

export type Blind = {
  id: string;
  name: string;
  level: number;
  group: string;
};

export type AirConditioning = {
  temperatureSetpoint: number;
  humiditySetpoint: number;
  actualTemperature: number;
  actualHumidity: number;
};

export type Ventilation = {
  co2Setpoint: number;
  actualCo2: number;
};

export type Amplifier = {
  on: boolean;
};

export type Room = Pick<
  DomesticRooms,
  "airConditioning" | "amplifier" | "blinds" | "id" | "lightingGroups" | "name" | "ventilation"
> & {
  group: RoomGroup;
};

export interface ShipArea {
  name: string;
  group: RoomGroup;
  rooms: Room[];
}

export interface ControlGroup<T> {
  name: string;
  controls: T[];
}

export type LightGroup = ControlGroup<DomesticLightingGroups>;
export type BlindsGroup = ControlGroup<DomesticBlinds>;

export type ActualAndSetpoint<T extends string> = `actual${Capitalize<T>}` | `${T}Setpoint`;

export type LogItem<T extends string> = {
  timestamp: Date;
} & {
  [K in ActualAndSetpoint<T>]: number;
};

export type AirConditioningLog = LogItem<"humidity" | "temperature">;
export type VentilationLog = LogItem<"co2">;

export type ValidateFn<T> = (value: T) => ValidationStatus;

export interface ValueObject<V> {
  value: V;
}

export type TimeValueTuple<V> = [time: Date, value: V];

export type NumValueObject = ValueObject<number>;

export type Thresholds = [lower: number, upper: number, ...other: number[]];
export type SafeRangeThresholds = [min: number, max: number];

export interface RoomState {
  co2: ValidationStatus;
  temperature: ValidationStatus;
  humidity: ValidationStatus;
  overall: ValidationStatus;
}

export interface RoomWithState {
  room: Room;
  state: RoomState;
}
