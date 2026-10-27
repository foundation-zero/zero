import { StringKeyOf } from "@/modules/common/types";
import { ComponentRecord, GraphQLRecord } from "@/modules/thrapp/lib/consts.types";
import { ExtractSimulationValues } from "../types";
import { SIMULATION, SimulationInputsOutputs } from "./consts";

export type SimulationInputsType<K extends string> = `${Capitalize<K>}SimulationInputsType`;
export type SimulationOutputsType<K extends string> = `${Capitalize<K>}SimulationOutputsType`;

// This creates a union type from the values of the inputs/outputs
// https://www.totaltypescript.com/tips/derive-a-union-type-from-an-object
export type ThrsSimulation<TDefinitions extends SimulationInputsOutputs = typeof SIMULATION> = {
  inputs: {
    [K in StringKeyOf<TDefinitions["inputs"]>]: GraphQLRecord<SimulationInputsType<K>> &
      ComponentRecord<ExtractSimulationValues<TDefinitions["inputs"][K]>>;
  }[StringKeyOf<TDefinitions["inputs"]>];
  outputs: {
    [K in StringKeyOf<TDefinitions["outputs"]>]: GraphQLRecord<SimulationOutputsType<K>> &
      ComponentRecord<ExtractSimulationValues<TDefinitions["outputs"][K]>>;
  }[StringKeyOf<TDefinitions["outputs"]>];
};

export const SIMULATION_TYPES = [
  "highTemperature",
  "thrusters",
  "pcm",
  "pvt",
  "adsorption",
  "consumers",
  "dhw",
  "dc",
  "drives",
  "thrs",
] as const;
export type ThrsSimulationType = (typeof SIMULATION_TYPES)[number];

export type THRSIM = {
  simulation: ThrsSimulation | null;
};
