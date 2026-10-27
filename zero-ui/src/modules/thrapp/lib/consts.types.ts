import { ChartDataType, RecordIndex, Stamped } from "@/modules/common/types";
import {
  ModuleDefinition,
  SchemaDefinition,
  SchemaDefinitions,
  THRSModule,
} from "@/modules/thrapp/types/thrs";
import { DEFINITIONS } from "./consts";

export type ThrsDefinitions<T extends Record<string, ModuleDefinition> = typeof DEFINITIONS> = T;

export type ThrsModules<
  TDefinitions extends Record<string, ModuleDefinition> = typeof DEFINITIONS,
> = {
  [K in keyof TDefinitions]: THRSModule<TDefinitions[K]>;
};

export type GraphQLRecord<K extends RecordIndex = RecordIndex> = {
  __typename?: K;
};

export type ComponentRecord<
  T extends Record<string, Stamped<ChartDataType>> = Record<string, Stamped<ChartDataType>>,
> = T;

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

export type THRS = {
  modules: ThrsModules;
};
