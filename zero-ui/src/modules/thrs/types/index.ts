import { Stamped, Unstamp } from "@common/types";
import { Ref, WritableComputedRef } from "vue";

export type SchemaDefinition<T> = {
  componentType: T;
};

export type SchemaDefinitions<T extends SchemaDefinition<unknown>> = Record<string, T>;

export type PumpControl = {
  dutypoint: Stamped<number>;
  on: Stamped<boolean>;
};

export type ValveControl = {
  setpoint: Stamped<number>;
};

export type PcmControl = {
  on: Stamped<boolean>;
};

export type HeatpumpControl = {
  dutypoint: Stamped<number>;
  on: Stamped<boolean>;
};

export type ControlFields = {
  [ControlComponentType.Pump]: (keyof PumpControl)[];
  [ControlComponentType.Valve]: (keyof ValveControl)[];
  [ControlComponentType.Pcm]: (keyof PcmControl)[];
  [ControlComponentType.Heatpump]: (keyof HeatpumpControl)[];
};

export type SensorFields = {
  [SensorComponentType.Flow]: (keyof FlowSensor)[];
  [SensorComponentType.Pressure]: (keyof PressureSensor)[];
  [SensorComponentType.Temperature]: (keyof TemperatureSensor)[];
  [SensorComponentType.Pump]: (keyof PumpSensor)[];
  [SensorComponentType.Valve]: (keyof Valve)[];
  [SensorComponentType.Thruster]: (keyof ThrusterSensor)[];
  [SensorComponentType.Pcs]: (keyof PcsSensor)[];
  [SensorComponentType.Pcm]: (keyof PcmSensor)[];
  [SensorComponentType.Level]: (keyof LevelSensor)[];
};

export type SimulationFields = {
  [SimulationComponentType.Temperature]: (keyof TemperatureBoundarySimulation)[];
  [SimulationComponentType.Thruster]: (keyof ThrusterSimulation)[];
  [SimulationComponentType.Pcs]: (keyof PcsSimulation)[];
  [SimulationComponentType.Boundary]: (keyof BoundarySimulation)[];
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

export type PcmSensor = {
  charged: Stamped<boolean>;
};

export type LevelSensor = {
  level: Stamped<number>;
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
  | PcsSensor
  | LevelSensor;

export type ControlType = PumpControl | ValveControl;

export type Sensors = Record<string, SensorType>;
export type Controls = Record<string, ControlType>;

export const enum ThrusterMode {
  Off = "OFF",
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
  Pcm = "pcm",
  Heatpump = "heatpump",
}

export const enum ValveType {
  Mix = "mix",
  FlowControl = "flowcontrol",
  Shutoff = "shutoff",
  Switch = "switch",
  Unknown = "null",
}

export type ControlDefinition<T extends ControlComponentType = ControlComponentType> =
  SchemaDefinition<T> & {
    yardTag: string;
  };

export type PumpControlDefinition = ControlDefinition<ControlComponentType.Pump>;
export type ValveControlDefinition = ControlDefinition<ControlComponentType.Valve> & {
  valveType: ValveType;
};

export type PcmControlDefinition = ControlDefinition<ControlComponentType.Pcm>;
export type HeatpumpControlDefinition = ControlDefinition<ControlComponentType.Heatpump>;

export type ControlDefinitions = SchemaDefinitions<
  PumpControlDefinition | ValveControlDefinition | PcmControlDefinition | HeatpumpControlDefinition
>;

export type ExtractControlValues<T extends ControlDefinitions> = PickMap<
  T,
  PumpControlDefinition,
  PumpControl
> &
  PickMap<T, ValveControlDefinition, ValveControl> &
  PickMap<T, PcmControlDefinition, PcmControl> &
  PickMap<T, HeatpumpControlDefinition, PumpControl>;

export const enum SensorComponentType {
  Temperature = "temperature",
  Pressure = "pressure",
  Flow = "flow",
  Pump = "pump",
  Valve = "valve",
  Thruster = "thruster",
  Pcs = "pcs",
  Pcm = "pcm",
  Level = "level",
}

export type THRSModule<TDefinition extends ModuleDefinition = ModuleDefinition> = {
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

export type SensorDefinition<T extends SensorComponentType = SensorComponentType> =
  SchemaDefinition<T> & {
    yardTag: string;
  };

export type TemperatureSensorDefinition = SensorDefinition<SensorComponentType.Temperature>;
export type PressureSensorDefinition = SensorDefinition<SensorComponentType.Pressure>;
export type FlowSensorDefinition = SensorDefinition<SensorComponentType.Flow>;
export type PumpSensorDefinition = SensorDefinition<SensorComponentType.Pump>;
export type ValveSensorDefinition = SensorDefinition<SensorComponentType.Valve> & {
  valveType: ValveType;
};
export type PcmSensorDefinition = SensorDefinition<SensorComponentType.Pcm>;
export type ThrusterSensorDefinition = SensorDefinition<SensorComponentType.Thruster>;
export type PcsSensorDefinition = SensorDefinition<SensorComponentType.Pcs>;
export type LevelSensorDefinition = SensorDefinition<SensorComponentType.Level>;

export type SensorDefinitions = SchemaDefinitions<SensorDefinition>;

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
  PickMap<T, PcsSensorDefinition, PcsSensor> &
  PickMap<T, PcmSensorDefinition, PcmSensor> &
  PickMap<T, LevelSensorDefinition, LevelSensor>;

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
  Enabled = "enabled",
  Ratio = "ratio",
  Dutypoint = "dutypoint",
  dT = "dT",
  Level = "level",
  Disabled = "disabled",
}

export type ParameterDefinition<T extends ParametersType = ParametersType> = SchemaDefinition<T>;

export type ParameterDefinitions = SchemaDefinitions<ParameterDefinition>;
export type TemperatureParameterDefinition = ParameterDefinition<ParametersType.Temperature>;
export type FlowParameterDefinition = ParameterDefinition<ParametersType.Flow>;
export type TuningParameterDefinition = ParameterDefinition<ParametersType.Tuning>;
export type EnabledParameterDefinition = ParameterDefinition<ParametersType.Enabled>;
export type RatioParameterDefinition = ParameterDefinition<ParametersType.Ratio>;
export type DutypointParameterDefinition = ParameterDefinition<ParametersType.Dutypoint>;
export type dTParameterDefinition = ParameterDefinition<ParametersType.dT>;
export type LevelParameterDefinition = ParameterDefinition<ParametersType.Level>;
export type DisabledParameterDefinition = ParameterDefinition<ParametersType.Disabled>;
export type Parameters = Record<string, number | PID>;

export type ExtractParameterValues<T extends ParameterDefinitions> = PickMap<
  T,
  TemperatureParameterDefinition,
  number
> &
  PickMap<T, FlowParameterDefinition, number> &
  PickMap<T, TuningParameterDefinition, PID> &
  PickMap<T, EnabledParameterDefinition, boolean> &
  PickMap<T, RatioParameterDefinition, number> &
  PickMap<T, DutypointParameterDefinition, number> &
  PickMap<T, dTParameterDefinition, number> &
  PickMap<T, LevelParameterDefinition, number> &
  PickMap<T, DisabledParameterDefinition, boolean>;

export type ThrusterSimulation = {
  heatFlow: Stamped<number>;
  active: Stamped<boolean>;
};

export type BoundarySimulation = {
  temperature: Stamped<number>;
  flow: Stamped<number>;
};

export type TemperatureSimulation = {
  temperature: Stamped<number>;
};

export type TemperatureBoundarySimulation = {
  temperature: Stamped<number>;
};

export type FlowSimulation = {
  flow: Stamped<number>;
};

export type PcsSimulation = ModeSelector<ThrusterMode>;

export const enum SimulationComponentType {
  Thruster = "thruster",
  Boundary = "boundary",
  Temperature = "temperature",
  Flow = "flow",
  Pcs = "pcs",
  HeatSource = "heatSource",
}

export type SimulationDefinition<T extends SimulationComponentType = SimulationComponentType> =
  SchemaDefinition<T>;

export type SimulationDefinitions = SchemaDefinitions<SimulationDefinition>;
export type ThrusterSimulationDefinition = SimulationDefinition<SimulationComponentType.Thruster>;
export type BoundarySimulationDefinition = SimulationDefinition<SimulationComponentType.Boundary>;
export type TemperatureSimulationDefinition =
  SimulationDefinition<SimulationComponentType.Temperature>;
export type FlowSimulationDefinition = SimulationDefinition<SimulationComponentType.Flow>;
export type PcsSimulationDefinition = SimulationDefinition<SimulationComponentType.Pcs>;

export type ExtractSimulationValues<T extends SimulationDefinitions> = PickMap<
  T,
  ThrusterSimulationDefinition,
  ThrusterSimulation
> &
  PickMap<T, BoundarySimulationDefinition, BoundarySimulation> &
  PickMap<T, TemperatureSimulationDefinition, TemperatureSimulation> &
  PickMap<T, FlowSimulationDefinition, FlowSimulation> &
  PickMap<T, PcsSimulationDefinition, PcsSimulation>;

export type ExtractAllValues<T extends SchemaDefinitions<SchemaDefinition<string>>> =
  T extends SensorDefinitions
    ? ExtractSensorValues<T>
    : T extends ControlDefinitions
      ? ExtractControlValues<T>
      : T extends ParameterDefinitions
        ? ExtractParameterValues<T>
        : T extends SimulationDefinitions
          ? ExtractSimulationValues<T>
          : never;
