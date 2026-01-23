import {
  ExtractSimulationValues,
  ModuleDefinition,
  SchemaDefinition,
  SchemaDefinitions,
  THRSModule,
} from "@/modules/thrs/types";
import { DEFINITIONS } from "./consts";

export type THRSDefinitions<T extends Record<string, ModuleDefinition> = typeof DEFINITIONS> = T;

export type THRSModules<
  TDefinitions extends Record<string, ModuleDefinition> = typeof DEFINITIONS,
> = {
  [K in keyof TDefinitions]: THRSModule<TDefinitions[K]>;
};

export type THRSSimulation<
  TDefinitions extends Record<string, ModuleDefinition> = typeof DEFINITIONS,
> = {
  inputs: {
    [K in keyof TDefinitions]: ExtractSimulationValues<TDefinitions[K]["simulation"]["inputs"]>;
  };
  outputs: {
    [K in keyof TDefinitions]: ExtractSimulationValues<TDefinitions[K]["simulation"]["outputs"]>;
  };
};

export type THRSQueries<
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

export type THRS = {
  modules: THRSModules;
  simulation: THRSSimulation;
};
