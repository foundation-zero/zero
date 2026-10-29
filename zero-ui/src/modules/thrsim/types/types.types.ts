import {
  AmcsControlMode,
  ControlDefinitions,
  ExtractControlValues,
  ExtractParameterValues,
  ExtractSensorValues,
  ExtractValues,
  ModeSelector,
  ParameterDefinitions,
  SchemaDefinition,
  SchemaDefinitions,
  SensorDefinitions,
  ThrusterMode,
} from "@/modules/thrapp/types/thrs";
import { Stamped } from "@common/types";
import { SimulationComponentType } from "./types.consts";

export type SimulationFields = {
  [SimulationComponentType.Temperature]: (keyof TemperatureBoundarySimulation)[];
  [SimulationComponentType.OverpressureTemperature]: (keyof OverpressureTemperatureSimulation)[];
  [SimulationComponentType.Thruster]: (keyof ThrusterSimulation)[];
  [SimulationComponentType.Pcs]: (keyof PcsSimulation)[];
  [SimulationComponentType.Boundary]: (keyof BoundarySimulation)[];
  [SimulationComponentType.HeatSource]: (keyof HeatSourceSimulation)[];
  [SimulationComponentType.ActiveHeatSource]: (keyof HeatSourceSimulation)[];
  [SimulationComponentType.Ugrid]: (keyof HeatSourceSimulation)[];
  [SimulationComponentType.PropulsionDrive]: (keyof HeatSourceSimulation)[];
  [SimulationComponentType.Flow]: (keyof FlowSimulation)[];
  [SimulationComponentType.HvacExchanger]: (keyof HvacExchangerSimulation)[];
  [SimulationComponentType.AdsorptionChiller]: (keyof AdsorptionChillerSimulation)[];
};

export type ThrusterSimulation = {
  heatFlow: Stamped<number>;
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

export type AdsorptionChillerSimulation = {
  freeCooling: Stamped<boolean>;
};

export type PcsSimulation = ModeSelector<ThrusterMode>;

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
  [SimulationComponentType.ActiveHeatSource]: HeatSourceSimulation;
  [SimulationComponentType.Ugrid]: HeatSourceSimulation;
  [SimulationComponentType.PropulsionDrive]: HeatSourceSimulation;
  [SimulationComponentType.HvacExchanger]: HvacExchangerSimulation;
  [SimulationComponentType.AmcsControlMode]: AmcsControlModeSimulation;
  [SimulationComponentType.AdsorptionChiller]: AdsorptionChillerSimulation;
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
