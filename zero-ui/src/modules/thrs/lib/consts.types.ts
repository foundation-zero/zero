import { RecordIndex, StringKeyOf } from "@/modules/common/types";
import {
  ExtractSimulationValues,
  ModuleDefinition,
  SchemaDefinition,
  SchemaDefinitions,
  THRSModule,
} from "@/modules/thrs/types";
import { DEFINITIONS, SIMULATION, SimulationInputsOutputs } from "./consts";

export type ThrsDefinitions<T extends Record<string, ModuleDefinition> = typeof DEFINITIONS> = T;

export type ThrsModules<
  TDefinitions extends Record<string, ModuleDefinition> = typeof DEFINITIONS,
> = {
  [K in keyof TDefinitions]: THRSModule<TDefinitions[K]>;
};

export type GraphQLRecord<
  K extends RecordIndex = RecordIndex,
  T extends Record<string, unknown> = Record<string, unknown>,
> = {
  __typename: K;
} & T;

export type SimulationInputsType<K extends string> = `${Capitalize<K>}SimulationInputsType`;
export type SimulationOutputsType<K extends string> = `${Capitalize<K>}SimulationOutputsType`;

// This creates a union type from the values of the inputs/outputs
// https://www.totaltypescript.com/tips/derive-a-union-type-from-an-object
export type ThrsSimulation<TDefinitions extends SimulationInputsOutputs = typeof SIMULATION> = {
  inputs: {
    [K in StringKeyOf<TDefinitions["inputs"]>]: GraphQLRecord<
      SimulationInputsType<K>,
      ExtractSimulationValues<TDefinitions["inputs"][K]>
    >;
  }[StringKeyOf<TDefinitions["inputs"]>];
  outputs: {
    [K in StringKeyOf<TDefinitions["outputs"]>]: GraphQLRecord<
      SimulationOutputsType<K>,
      ExtractSimulationValues<TDefinitions["outputs"][K]>
    >;
  }[StringKeyOf<TDefinitions["outputs"]>];
};

export type ThrsQueries<
  TDefinitions extends Record<string, ModuleDefinition> = typeof DEFINITIONS,
> = {
  [Module in keyof TDefinitions]: {
    [QueryGroup in keyof TDefinitions[Module]]: TDefinitions[Module][QueryGroup] extends Record<
      string,
      SchemaDefinitions<SchemaDefinition<unknown>>
    >
      ? {
          [DefinitionPart in keyof TDefinitions[Module][QueryGroup]]: string;
        }
      : string;
  };
};

export const SIMULATION_TYPES = [
  "highTemperature",
  "thrusters",
  "pcm",
  "pvt",
  "adsorption",
  "consumers",
  "dc",
  "dhw",
  "drives",
] as const;
export type ThrsSimulationType = (typeof SIMULATION_TYPES)[number];

export type THRS = {
  modules: ThrsModules;
  simulation: ThrsSimulation | null;
};
