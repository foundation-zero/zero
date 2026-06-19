import { Stamped, Unstamp } from "@common/types";
import { Ref, WritableComputedRef } from "vue";

export type SchemaDefinition<T> = {
  componentType: T;
};

// Number between 0 and 1 representing a ratio (e.g., for flow distribution)
export type Ratio = number;

export type SchemaDefinitions<T extends SchemaDefinition<unknown>> = Record<string, T>;

export const enum BoilerTankState {
  InUse = "IN_USE",
  Filling = "FILLING",
  Boosting = "BOOSTING",
  Disabled = "DISABLED",
  NeedsBoost = "NEEDS_BOOST",
  NeedsFill = "NEEDS_FILL",
  Standby = "STANDBY",
}

export type BoilerTankController = {
  tank1State: Stamped<BoilerTankState>;
  tank2State: Stamped<BoilerTankState>;
  tank3State: Stamped<BoilerTankState>;
  timeToFill: Stamped<number>;
};

export type PIDController = {
  setpoint: Stamped<number>;
  measurement: Stamped<number | undefined>;
  output: Stamped<number | undefined>;
  error: Stamped<number | undefined>;
  enabled: Stamped<boolean>;
  tuning: Stamped<PID>;
  components: Stamped<PID>;
};

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
  [ControlComponentType.BoilersTanksController]: (keyof BoilerTankController)[];
  [ControlComponentType.PIDController]: (keyof PIDController)[];
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
  [SimulationComponentType.OverpressureTemperature]: (keyof OverpressureTemperatureSimulation)[];
  [SimulationComponentType.Thruster]: (keyof ThrusterSimulation)[];
  [SimulationComponentType.Pcs]: (keyof PcsSimulation)[];
  [SimulationComponentType.Boundary]: (keyof BoundarySimulation)[];
  [SimulationComponentType.HeatSource]: (keyof HeatSourceSimulation)[];
};

export type PumpSensor = {
  flow: Stamped<Ratio>;
  speed: Stamped<number>;
  opTime: Stamped<number>;
};

export type TemperatureSensor = {
  temperature: Stamped<number>;
};

export type DeltaTSensor = {
  deltaT: Stamped<number>;
};

export type HeatExchangerSensor = DeltaTSensor & {
  heat: Stamped<number>;
};

export type Valve = {
  positionRel: Stamped<Ratio>;
};

export type FlowSensor = {
  flow: Stamped<Ratio>;
  temperature: Stamped<number>;
};

export type CalculatedFlowSensor = {
  flow: Stamped<Ratio>;
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
  | LevelSensor
  | DeltaTSensor;

export type ControlType =
  | PumpControl
  | ValveControl
  | PcmControl
  | HeatpumpControl
  | BoilerTankController
  | PIDController;

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
  BoilersTanksController = "boilersTanksController",
  PIDController = "pidController",
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
export type BoilerTankControllerDefinition =
  ControlDefinition<ControlComponentType.BoilersTanksController>;
export type PIDControllerDefinition = ControlDefinition<ControlComponentType.PIDController>;

export type ControlDefinitions = SchemaDefinitions<
  | PumpControlDefinition
  | ValveControlDefinition
  | PcmControlDefinition
  | HeatpumpControlDefinition
  | BoilerTankControllerDefinition
  | PIDControllerDefinition
>;

export type ControlDefinitionMap = {
  [ControlComponentType.Pump]: PumpControl;
  [ControlComponentType.Valve]: ValveControl;
  [ControlComponentType.Pcm]: PcmControl;
  [ControlComponentType.Heatpump]: HeatpumpControl;
  [ControlComponentType.BoilersTanksController]: BoilerTankController;
  [ControlComponentType.PIDController]: PIDController;
};

export type ExtractControlValues<T extends ControlDefinitions> = ExtractValues<
  T,
  ControlDefinitionMap
>;

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
  DeltaT = "deltaT",
  HeatExchanger = "heatExchanger",
  CalculatedFlow = "calculatedFlow",
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

export type SensorDefinitionMap = {
  [SensorComponentType.Temperature]: TemperatureSensor;
  [SensorComponentType.Pressure]: PressureSensor;
  [SensorComponentType.Flow]: FlowSensor;
  [SensorComponentType.Pump]: PumpSensor;
  [SensorComponentType.Valve]: Valve;
  [SensorComponentType.Pcm]: PcmSensor;
  [SensorComponentType.Thruster]: ThrusterSensor;
  [SensorComponentType.Pcs]: PcsSensor;
  [SensorComponentType.Level]: LevelSensor;
  [SensorComponentType.DeltaT]: DeltaTSensor;
  [SensorComponentType.HeatExchanger]: HeatExchangerSensor;
  [SensorComponentType.CalculatedFlow]: CalculatedFlowSensor;
};

export type ExtractValues<
  T extends Record<string, unknown>,
  Map extends Record<string, unknown>,
> = {
  [K in keyof T as T[K] extends { componentType: infer C }
    ? C extends keyof Map
      ? K
      : never
    : never]: T[K] extends { componentType: infer C }
    ? C extends keyof Map
      ? Map[C]
      : never
    : never;
};

export type ExtractSensorValues<T extends SensorDefinitions> = ExtractValues<
  T,
  SensorDefinitionMap
>;

export type StringKeys<T extends Record<string, unknown>> = {
  [K in keyof T as K extends string ? K : never]: T[K];
};

export type PickMap<T extends Record<string, unknown>, FromType, ToType> = {
  [K in keyof StringKeys<T> as T[K] extends FromType ? K : never]: ToType;
};

export type PickKeys<T extends Record<string, unknown>, Type> = keyof {
  [K in keyof StringKeys<T> as T[K] extends Type ? K : never]: T[K];
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
export type ParameterType = number | PID;
export type Parameters = Record<string, ParameterType>;

export type ParameterDefinitionMap = {
  [ParametersType.Temperature]: number;
  [ParametersType.Flow]: number;
  [ParametersType.Tuning]: PID;
  [ParametersType.Enabled]: boolean;
  [ParametersType.Ratio]: number;
  [ParametersType.Dutypoint]: number;
  [ParametersType.dT]: number;
  [ParametersType.Level]: number;
  [ParametersType.Disabled]: boolean;
};

export type ExtractParameterValues<T extends ParameterDefinitions> = ExtractValues<
  T,
  ParameterDefinitionMap
>;

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

export type OverpressureTemperatureSimulation = {
  temperature: Stamped<number>;
  overpressure: Stamped<number>;
};

export type FlowSimulation = {
  flow: Stamped<number>;
};

export type HeatSourceSimulation = {
  heatFlow: Stamped<number>;
};

export type PcsSimulation = ModeSelector<ThrusterMode>;

export const enum SimulationComponentType {
  Thruster = "thruster",
  Boundary = "boundary",
  Temperature = "temperature",
  OverpressureTemperature = "overpressureTemperature",
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
export type OverpressureTemperatureSimulationDefinition =
  SimulationDefinition<SimulationComponentType.OverpressureTemperature>;
export type FlowSimulationDefinition = SimulationDefinition<SimulationComponentType.Flow>;
export type PcsSimulationDefinition = SimulationDefinition<SimulationComponentType.Pcs>;
export type HeatSourceSimulationDefinition =
  SimulationDefinition<SimulationComponentType.HeatSource>;

export type SimulationDefinitionMap = {
  [SimulationComponentType.Thruster]: ThrusterSimulation;
  [SimulationComponentType.Boundary]: BoundarySimulation;
  [SimulationComponentType.Temperature]: TemperatureSimulation;
  [SimulationComponentType.OverpressureTemperature]: OverpressureTemperatureSimulation;
  [SimulationComponentType.Flow]: FlowSimulation;
  [SimulationComponentType.Pcs]: PcsSimulation;
  [SimulationComponentType.HeatSource]: HeatSourceSimulation;
};

export type ExtractSimulationValues<T extends SimulationDefinitions> = ExtractValues<
  T,
  SimulationDefinitionMap
>;

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
