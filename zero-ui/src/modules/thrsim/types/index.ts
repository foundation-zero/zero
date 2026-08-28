import { Stamped, Unstamp } from "@common/types";
import { Ref, WritableComputedRef } from "vue";

export type SchemaDefinition<T> = {
  componentType: T;
};

// Number between 0 and 1 representing a ratio (e.g., for flow distribution)
export type Ratio = number;

// Number between 0 and 360 representing a degree (°)
export type Degree = number;

export type SchemaDefinitions<T extends SchemaDefinition<unknown>> = Record<string, T>;

export const enum AmcsControlMode {
  Local = "LOCAL",
  Manual = "MANUAL",
  Auto = "AUTO",
  External = "EXTERNAL",
}

export const enum BoilerTankState {
  InUse = "IN_USE",
  Filling = "FILLING",
  Boosting = "BOOSTING",
  Disabled = "DISABLED",
  NeedsBoost = "NEEDS_BOOST",
  NeedsFill = "NEEDS_FILL",
  Standby = "STANDBY",
}

export type DhwTankController = {
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

export const enum PvtMode {
  Idle = "IDLE",
  Harvesting = "HARVESTING",
}

export type PvtController = {
  mode: Stamped<PvtMode>;
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
  temperatureSetpoint: Stamped<number>;
  on: Stamped<boolean>;
};

export type AdsorptionChillerControl = {
  enable: Stamped<boolean>;
};

export type ControlValueFields =
  | keyof PumpControl
  | keyof ValveControl
  | keyof PcmControl
  | keyof HeatpumpControl;

export type ControlFields = {
  [ControlComponentType.Pump]: (keyof PumpControl)[];
  [ControlComponentType.Valve]: (keyof ValveControl)[];
  [ControlComponentType.Pcm]: (keyof PcmControl)[];
  [ControlComponentType.Heatpump]: (keyof HeatpumpControl)[];
};

export type ControllerStateFields = {
  [ControllerStateComponentType.DhwTanksController]: (keyof DhwTankController)[];
  [ControllerStateComponentType.PIDController]: (keyof PIDController)[];
};

export type ControllerFields = keyof DhwTankController | keyof PIDController;

export type SensorValueFields =
  | keyof PumpSensor
  | keyof TemperatureSensor
  | keyof FlowSensor
  | keyof PressureSensor
  | keyof ThrusterSensor
  | keyof PcsSensor
  | keyof LevelSensor
  | keyof DeltaTSensor
  | keyof HeatExchangerSensor
  | keyof Valve
  | keyof LevelSwitchSensor;

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
  [SensorComponentType.LevelSwitch]: (keyof LevelSwitchSensor)[];
};

export type SimulationFields = {
  [SimulationComponentType.Temperature]: (keyof TemperatureBoundarySimulation)[];
  [SimulationComponentType.OverpressureTemperature]: (keyof OverpressureTemperatureSimulation)[];
  [SimulationComponentType.Thruster]: (keyof ThrusterSimulation)[];
  [SimulationComponentType.Pcs]: (keyof PcsSimulation)[];
  [SimulationComponentType.Boundary]: (keyof BoundarySimulation)[];
  [SimulationComponentType.HeatSource]: (keyof HeatSourceSimulation)[];
  [SimulationComponentType.Flow]: (keyof FlowSimulation)[];
  [SimulationComponentType.HvacExchanger]: (keyof HvacExchangerSimulation)[];
};

export type PumpSensor = {
  dutypoint: Stamped<Ratio>;
  on: Stamped<boolean>;
  flow: Stamped<Ratio>;
  speed: Stamped<number>;
  opTime: Stamped<number>;
  pressure: Stamped<number>;
  energyConsumption: Stamped<number>;
  powerInput: Stamped<number>;
};

export type TemperatureSensor = {
  temperature: Stamped<number>;
};

export type CalculatedTemperatureSensor = {
  temperature: Stamped<number | undefined>;
};

export type DeltaTSensor = {
  deltaT: Stamped<number>;
};

export type HeatExchangerSensor = DeltaTSensor & {
  heat: Stamped<number>;
};

export type Valve = {
  positionRel: Stamped<Ratio>;
  positionAbs: Stamped<Degree>;
};

export type FlowSensor = {
  flow: Stamped<Ratio>;
  temperature: Stamped<number>;
  quantity: Stamped<number>;
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

export type LevelSwitchSensor = {
  empty: Stamped<boolean>;
};

export type ThrusterSensor = Toggle;
export type BrightloopSensor = Toggle;
export type UgridSensor = Toggle;
export type PropulsionDriveSensor = Toggle;
export type ShorePowerConverterSensor = Toggle;
export type IrradianceSensor = {
  irradiance: Stamped<number>;
};

export type PcsSensor = ModeSelector<string>;

export type AdsorptionChillerSensor = {
  operating: Stamped<boolean>;
  noError: Stamped<boolean>;
  freeCooling: Stamped<boolean>;
};

export type AmcsControlModeSensor = {
  mode: Stamped<AmcsControlMode>;
};

export type SensorType =
  | PumpSensor
  | TemperatureSensor
  | Valve
  | FlowSensor
  | PressureSensor
  | ThrusterSensor
  | PcsSensor
  | LevelSensor
  | LevelSwitchSensor
  | DeltaTSensor
  | AdsorptionChillerSensor
  | BrightloopSensor
  | UgridSensor
  | PropulsionDriveSensor
  | ShorePowerConverterSensor
  | IrradianceSensor;

export type ControlType =
  | PumpControl
  | ValveControl
  | PcmControl
  | HeatpumpControl
  | AdsorptionChillerControl;

export type ControllerStateType = DhwTankController | PIDController;
export type Sensors = Record<string, SensorType>;
export type Controls = Record<string, ControlType>;
export type ControllerState = Record<string, ControllerStateType>;

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
  Pump = "control:pump",
  Valve = "control:valve",
  Pcm = "control:pcm",
  Heatpump = "control:heatpump",
  AdsorptionChiller = "control:adsorptionChiller",
}

export const CONTROL_COMPONENT_TYPES = [
  ControlComponentType.Pump,
  ControlComponentType.Valve,
  ControlComponentType.Pcm,
  ControlComponentType.Heatpump,
];

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
export type AdsorptionChillerControlDefinition =
  ControlDefinition<ControlComponentType.AdsorptionChiller>;

export type ControlDefinitions = SchemaDefinitions<
  | PumpControlDefinition
  | ValveControlDefinition
  | PcmControlDefinition
  | HeatpumpControlDefinition
  | AdsorptionChillerControlDefinition
>;

export type ControlDefinitionMap = {
  [ControlComponentType.Pump]: PumpControl;
  [ControlComponentType.Valve]: ValveControl;
  [ControlComponentType.Pcm]: PcmControl;
  [ControlComponentType.Heatpump]: HeatpumpControl;
  [ControlComponentType.AdsorptionChiller]: AdsorptionChillerControl;
};

export type ControlValues<T extends ControlComponentType> = {
  [K in keyof ControlDefinitionMap[T]]: Unstamp<ControlDefinitionMap[T][K]>;
};

export type ExtractControlValues<T extends ControlDefinitions> = ExtractValues<
  T,
  ControlDefinitionMap
>;

export const enum ControllerStateComponentType {
  DhwTanksController = "controller:dhwTanksController",
  PIDController = "pidController",
  PvtController = "pvtController",
}

export type ControllerStateDefinition<
  T extends ControllerStateComponentType = ControllerStateComponentType,
> = SchemaDefinition<T>;

export type DhwTankControllerDefinition =
  ControllerStateDefinition<ControllerStateComponentType.DhwTanksController>;
export type PIDControllerDefinition =
  ControllerStateDefinition<ControllerStateComponentType.PIDController>;
export type PvtControllerDefinition =
  ControllerStateDefinition<ControllerStateComponentType.PvtController>;

export type ControllerStateDefinitions = SchemaDefinitions<
  DhwTankControllerDefinition | PIDControllerDefinition | PvtControllerDefinition
>;

export type ControllerStateDefinitionMap = {
  [ControllerStateComponentType.DhwTanksController]: DhwTankController;
  [ControllerStateComponentType.PIDController]: PIDController;
  [ControllerStateComponentType.PvtController]: PvtController;
};

export type ExtractControllerState<T extends ControllerStateDefinitions> = ExtractValues<
  T,
  ControllerStateDefinitionMap
>;

export const enum SensorComponentType {
  Temperature = "sensor:temperature",
  CalculatedTemperature = "sensor:calculatedTemperature",
  Pressure = "sensor:pressure",
  Irradiance = "sensor:irradiance",
  Flow = "sensor:flow",
  Pump = "sensor:pump",
  Valve = "sensor:valve",
  Thruster = "sensor:thruster",
  Pcs = "sensor:pcs",
  Pcm = "sensor:pcm",
  Level = "sensor:level",
  LevelSwitch = "sensor:levelSwitch",
  DeltaT = "sensor:deltaT",
  HeatExchanger = "sensor:heatExchanger",
  CalculatedFlow = "sensor:calculatedFlow",
  AdsorptionChiller = "sensor:adsorptionChiller",
  Brightloop = "sensor:brightloop",
  Ugrid = "sensor:ugrid",
  PropulsionDrive = "sensor:propulsionDrive",
  ShorePowerConverter = "sensor:shorePowerConverter",
  AmcsControlMode = "system:amcsControlMode",
}

export const SENSOR_COMPONENT_TYPES = [
  SensorComponentType.Temperature,
  SensorComponentType.CalculatedTemperature,
  SensorComponentType.Pressure,
  SensorComponentType.Flow,
  SensorComponentType.Pump,
  SensorComponentType.Valve,
  SensorComponentType.Thruster,
  SensorComponentType.Pcs,
  SensorComponentType.Pcm,
  SensorComponentType.Level,
  SensorComponentType.LevelSwitch,
  SensorComponentType.DeltaT,
  SensorComponentType.HeatExchanger,
  SensorComponentType.CalculatedFlow,
  SensorComponentType.Brightloop,
  SensorComponentType.Ugrid,
  SensorComponentType.PropulsionDrive,
  SensorComponentType.ShorePowerConverter,
  SensorComponentType.Irradiance,
];

export type THRSModule<TDefinition extends ModuleDefinition = ModuleDefinition> = {
  sensorValues: ExtractSensorValues<TDefinition["sensorValues"]>;
  controlValues: ExtractControlValues<TDefinition["controlValues"]>;
  parameters: ExtractParameterValues<TDefinition["parameters"]>;
  controllerState: ExtractControllerState<TDefinition["controllerState"]>;
};

export type ModuleDefinition<
  TSensors extends SensorDefinitions = SensorDefinitions,
  TControls extends ControlDefinitions = ControlDefinitions,
  TParameters extends ParameterDefinitions = ParameterDefinitions,
  TControllerState extends ControllerStateDefinitions = ControllerStateDefinitions,
> = {
  sensorValues: TSensors;
  controlValues: TControls;
  parameters: TParameters;
  controllerState: TControllerState;
};

export type SensorDefinition<T extends SensorComponentType = SensorComponentType> =
  SchemaDefinition<T> & {
    yardTag?: string;
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
export type DeltaTSensorDefinition = SensorDefinition<SensorComponentType.DeltaT>;
export type HeatExchangerSensorDefinition = SensorDefinition<SensorComponentType.HeatExchanger>;
export type CalculatedFlowSensorDefinition = SensorDefinition<SensorComponentType.CalculatedFlow>;

export type SensorDefinitions = SchemaDefinitions<SensorDefinition>;

export type SensorDefinitionMap = {
  [SensorComponentType.Temperature]: TemperatureSensor;
  [SensorComponentType.CalculatedTemperature]: CalculatedTemperatureSensor;
  [SensorComponentType.Pressure]: PressureSensor;
  [SensorComponentType.Flow]: FlowSensor;
  [SensorComponentType.Pump]: PumpSensor;
  [SensorComponentType.Valve]: Valve;
  [SensorComponentType.Pcm]: PcmSensor;
  [SensorComponentType.Thruster]: ThrusterSensor;
  [SensorComponentType.Pcs]: PcsSensor;
  [SensorComponentType.Level]: LevelSensor;
  [SensorComponentType.LevelSwitch]: LevelSwitchSensor;
  [SensorComponentType.DeltaT]: DeltaTSensor;
  [SensorComponentType.HeatExchanger]: HeatExchangerSensor;
  [SensorComponentType.CalculatedFlow]: CalculatedFlowSensor;
  [SensorComponentType.AdsorptionChiller]: AdsorptionChillerSensor;
  [SensorComponentType.Brightloop]: BrightloopSensor;
  [SensorComponentType.Ugrid]: UgridSensor;
  [SensorComponentType.PropulsionDrive]: PropulsionDriveSensor;
  [SensorComponentType.ShorePowerConverter]: ShorePowerConverterSensor;
  [SensorComponentType.Irradiance]: IrradianceSensor;
  [SensorComponentType.AmcsControlMode]: AmcsControlModeSensor;
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
  Temperature = "parameter:temperature",
  Flow = "parameter:flow",
  FlowControl = "parameter:flowcontrol",
  Tuning = "parameter:tuning",
  Enabled = "parameter:enabled",
  Ratio = "parameter:ratio",
  Dutypoint = "parameter:dutypoint",
  dT = "parameter:dT",
  Level = "parameter:level",
}

export const PARAMETERS_TYPES = [
  ParametersType.Temperature,
  ParametersType.Flow,
  ParametersType.FlowControl,
  ParametersType.Tuning,
  ParametersType.Enabled,
  ParametersType.Ratio,
  ParametersType.Dutypoint,
  ParametersType.dT,
  ParametersType.Level,
];

export type ParameterDefinition<T extends ParametersType = ParametersType> = SchemaDefinition<T>;

export type ParameterDefinitions = SchemaDefinitions<ParameterDefinition>;
export type TemperatureParameterDefinition = ParameterDefinition<ParametersType.Temperature>;
export type FlowParameterDefinition = ParameterDefinition<ParametersType.Flow>;
export type FlowControlParameterDefinition = ParameterDefinition<ParametersType.FlowControl>;
export type TuningParameterDefinition = ParameterDefinition<ParametersType.Tuning>;
export type EnabledParameterDefinition = ParameterDefinition<ParametersType.Enabled>;
export type RatioParameterDefinition = ParameterDefinition<ParametersType.Ratio>;
export type DutypointParameterDefinition = ParameterDefinition<ParametersType.Dutypoint>;
export type dTParameterDefinition = ParameterDefinition<ParametersType.dT>;
export type LevelParameterDefinition = ParameterDefinition<ParametersType.Level>;
export type ParameterType = number | PID | boolean;
export type Parameters = Record<string, ParameterType>;

export type ParameterDefinitionMap = {
  [ParametersType.Temperature]: number;
  [ParametersType.Flow]: number;
  [ParametersType.FlowControl]: Ratio;
  [ParametersType.Tuning]: PID;
  [ParametersType.Enabled]: boolean;
  [ParametersType.Ratio]: Ratio;
  [ParametersType.Dutypoint]: Ratio;
  [ParametersType.dT]: number;
  [ParametersType.Level]: number;
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

export type HvacExchangerSimulation = {
  heatFlow: Stamped<number>;
  maximumTemperature: Stamped<number>;
};

export type AmcsControlModeSimulation = {
  mode: Stamped<AmcsControlMode>;
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
  HvacExchanger = "hvacExchanger",
  AmcsControlMode = "amcsControlMode",
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
  [SimulationComponentType.HvacExchanger]: HvacExchangerSimulation;
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
