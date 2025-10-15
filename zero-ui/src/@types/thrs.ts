import { Ref, WritableComputedRef } from "vue";

export type Stamped<T> = { value: T; timestamp: Date };
export type Unstamp<T> = T extends Stamped<infer U> ? U : never;

export type PumpControl = {
  dutypoint: Stamped<number>;
  on: Stamped<boolean>;
};

export type ValveControl = {
  setpoint: Stamped<number>;
};

export type ControlFields = {
  [ControlComponentType.Pump]: (keyof PumpControl)[];
  [ControlComponentType.Valve]: (keyof ValveControl)[];
};

export type SensorFields = {
  [SensorComponentType.Flow]: (keyof FlowSensor)[];
  [SensorComponentType.Pressure]: (keyof PressureSensor)[];
  [SensorComponentType.Temperature]: (keyof TemperatureSensor)[];
  [SensorComponentType.Pump]: (keyof PumpSensor)[];
  [SensorComponentType.Valve]: (keyof Valve)[];
  [SensorComponentType.Thruster]: (keyof ThrusterSensor)[];
  [SensorComponentType.Pcs]: (keyof PcsSensor)[];
};

export type PumpSensor = {
  flow: Stamped<number>;
  speed: Stamped<number>;
  opTime: Stamped<number>;
};

export type TemperatureSensor = {
  temperature: Stamped<number>;
};

export type Valve = {
  positionRel: Stamped<number>;
};

export type FlowSensor = {
  flow: Stamped<number>;
  temperature: Stamped<number>;
};

export type PressureSensor = {
  pressure: Stamped<number>;
};

export type Toggle = {
  active: Stamped<boolean>;
};

export type ModeSelector<T> = {
  mode: Stamped<T>;
};

export type ThrusterSensor = Toggle;
export type PcsSensor = ModeSelector<string>;

export type SensorType =
  | PumpSensor
  | TemperatureSensor
  | Valve
  | FlowSensor
  | PressureSensor
  | ThrusterSensor
  | PcsSensor;

export type ControlType = PumpControl | ValveControl;

export type Sensors = Record<string, SensorType>;
export type Controls = Record<string, ControlType>;

export const enum ThrusterMode {
  OFF = "OFF",
  Propulsion = "PROPULSION",
  Maneuvering = "MANEUVERING",
  Regeneration = "REGENERATION",
}

type FormValue<T> = {
  value: WritableComputedRef<T>;
  isDirty: Ref<boolean>;
};

export type ControlForm<Type extends Record<string, Stamped<unknown>>> = {
  [K in keyof Type]: FormValue<Unstamp<Type[K]>>;
} & {
  isSubmitting: Ref<boolean>;
  error: Ref<null | string>;
  commit: () => Promise<void>;
};

export const enum ControlComponentType {
  Pump = "pump",
  Valve = "valve",
}

export const enum ValveType {
  Mix = "mix",
  FlowControl = "flowcontrol",
  Shutoff = "shutoff",
  Switch = "switch",
}

export type ControlDefinition<T extends ControlComponentType = ControlComponentType> = {
  yardTag: string;
  componentType: T;
};

export type PumpControlDefinition = ControlDefinition<ControlComponentType.Pump>;
export type ValveControlDefinition = ControlDefinition<ControlComponentType.Valve> & {
  valveType: ValveType;
};

export type ControlDefinitions = Record<string, PumpControlDefinition | ValveControlDefinition>;

export type ExtractControlValues<T extends ControlDefinitions> = PickMap<
  T,
  PumpControlDefinition,
  PumpControl
> &
  PickMap<T, ValveControlDefinition, ValveControl>;

export const enum SensorComponentType {
  Temperature = "temperature",
  Pressure = "pressure",
  Flow = "flow",
  Pump = "pump",
  Valve = "valve",
  Thruster = "thruster",
  Pcs = "pcs",
}

export type THRSModule<TDefinition extends ModuleDefinition> = {
  sensorValues: ExtractSensorValues<TDefinition["sensorValues"]>;
  controlValues: ExtractControlValues<TDefinition["controlValues"]>;
  parameters: ExtractParameterValues<TDefinition["parameters"]>;
};

export type ModuleDefinition<
  TSensors extends SensorDefinitions = SensorDefinitions,
  TControls extends ControlDefinitions = ControlDefinitions,
  TParameters extends ParameterDefinitions = ParameterDefinitions,
> = {
  sensorValues: TSensors;
  controlValues: TControls;
  parameters: TParameters;
};

export type SensorDefinition<T extends SensorComponentType = SensorComponentType> = {
  yardTag: string;
  componentType: T;
};

export type TemperatureSensorDefinition = SensorDefinition<SensorComponentType.Temperature>;
export type PressureSensorDefinition = SensorDefinition<SensorComponentType.Pressure>;
export type FlowSensorDefinition = SensorDefinition<SensorComponentType.Flow>;
export type PumpSensorDefinition = SensorDefinition<SensorComponentType.Pump>;
export type ValveSensorDefinition = SensorDefinition<SensorComponentType.Valve> & {
  valveType: ValveType;
};
export type ThrusterSensorDefinition = SensorDefinition<SensorComponentType.Thruster>;
export type PcsSensorDefinition = SensorDefinition<SensorComponentType.Pcs>;

export type SensorDefinitions = Record<string, SensorDefinition>;

export type ExtractSensorValues<T extends SensorDefinitions> = PickMap<
  T,
  TemperatureSensorDefinition,
  TemperatureSensor
> &
  PickMap<T, PressureSensorDefinition, PressureSensor> &
  PickMap<T, FlowSensorDefinition, FlowSensor> &
  PickMap<T, PumpSensorDefinition, PumpSensor> &
  PickMap<T, ValveSensorDefinition, Valve> &
  PickMap<T, ThrusterSensorDefinition, ThrusterSensor> &
  PickMap<T, PcsSensorDefinition, PcsSensor>;

export type StringKeys<T extends Record<string, unknown>> = {
  [K in keyof T as K extends string ? K : never]: T[K];
};

export type PickMap<T extends Record<string, unknown>, FromType, ToType> = {
  [K in keyof StringKeys<T> as T[K] extends FromType ? K : never]: ToType;
};

export type PID = [proportional: number, integral: number, derivative: number];

export const enum ParametersType {
  Temperature = "temperature",
  Flow = "flow",
  Tuning = "tuning",
}

export type ParameterDefinition<T extends ParametersType = ParametersType> = {
  componentType: T;
};

export type ParameterDefinitions = Record<string, ParameterDefinition>;
export type TemperatureParameterDefinition = ParameterDefinition<ParametersType.Temperature>;
export type FlowParameterDefinition = ParameterDefinition<ParametersType.Flow>;
export type TuningParameterDefinition = ParameterDefinition<ParametersType.Tuning>;
export type Parameters = Record<string, number | PID>;

export type ExtractParameterValues<T extends ParameterDefinitions> = PickMap<
  T,
  TemperatureParameterDefinition,
  number
> &
  PickMap<T, FlowParameterDefinition, number> &
  PickMap<T, TuningParameterDefinition, PID>;

export type Field<T> = Record<string, Stamped<T>>;
export type Component = Record<string, Field<number>>;
