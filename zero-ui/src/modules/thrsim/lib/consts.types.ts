import { StringKeyOf } from "@/modules/common/types";
import { ComponentRecord } from "@/modules/thrapp/lib/consts.types";
import { ExtractSimulationValues } from "../types";
import { SIMULATION, SimulationInputsOutputs } from "./consts";

// This creates a union type from the values of the inputs/outputs
// https://www.totaltypescript.com/tips/derive-a-union-type-from-an-object
export type ThrsSimulation<TDefinitions extends SimulationInputsOutputs = typeof SIMULATION> = {
  inputs: {
    [K in StringKeyOf<TDefinitions["inputs"]>]: ComponentRecord<
      ExtractSimulationValues<TDefinitions["inputs"][K]>
    >;
  }[StringKeyOf<TDefinitions["inputs"]>];
  outputs: {
    [K in StringKeyOf<TDefinitions["outputs"]>]: ComponentRecord<
      ExtractSimulationValues<TDefinitions["outputs"][K]>
    >;
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

export type SimulatorStatus = {
  status: "AVAILABLE" | "RUNNING" | "STEPPING";
  // The thrs-control mode, a simulation type in snake_case.
  mode: string;
  simulationTime: string;
};

// The MQTT GraphQL API's answer to `SIMULATOR_QUERY`.
export type Simulator = {
  thrs: {
    simulator: {
      status: SimulatorStatus | null;
      simulationInputs: ThrsSimulation["inputs"] | null;
      simulationOutputs: ThrsSimulation["outputs"] | null;
    } | null;
  } | null;
};
