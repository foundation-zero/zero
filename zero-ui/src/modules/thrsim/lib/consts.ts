import { ThrusterMode } from "@/modules/thrapp/types/thrs";
import { gql } from "@urql/vue";
import { SimulationComponentType, SimulationDefinitions, SimulationFields } from "../types";
import * as Definitions from "./consts.generated";
import { SimulationInputsType, SimulationOutputsType, ThrsSimulationType } from "./consts.types";
import * as Queries from "./queries.generated";

export * from "./consts.types";

export const THRUSTER_MODES: ThrusterMode[] = [
  ThrusterMode.Maneuvering,
  ThrusterMode.Off,
  ThrusterMode.Propulsion,
  ThrusterMode.Regeneration,
];

export type SimulationInputsOutputs<
  TInput extends Record<string, SimulationDefinitions> = Record<string, SimulationDefinitions>,
  TOutput extends Record<string, SimulationDefinitions> = Record<string, SimulationDefinitions>,
> = {
  inputs: TInput;
  outputs: TOutput;
};

export const toSimulation = <
  TInput extends Record<ThrsSimulationType, SimulationDefinitions>,
  TOutput extends Record<ThrsSimulationType, SimulationDefinitions>,
>(
  input: TInput,
  output: TOutput,
): SimulationInputsOutputs<TInput, TOutput> => ({
  inputs: input,
  outputs: output,
});

export const SIMULATION = toSimulation(
  {
    highTemperature: Definitions.HIGH_TEMPERATURE_SIMULATION_INPUTS,
    thrusters: Definitions.THRUSTERS_SIMULATION_INPUTS,
    pcm: Definitions.PCM_SIMULATION_INPUTS,
    pvt: Definitions.PVT_SIMULATION_INPUTS,
    adsorption: Definitions.ADSORPTION_SIMULATION_INPUTS,
    consumers: Definitions.CONSUMERS_SIMULATION_INPUTS,
    dc: Definitions.DC_SIMULATION_INPUTS,
    dhw: Definitions.DHW_SIMULATION_INPUTS,
    drives: Definitions.DRIVES_SIMULATION_INPUTS,
    thrs: Definitions.THRS_SIMULATION_INPUTS,
  },
  {
    highTemperature: Definitions.HIGH_TEMPERATURE_SIMULATION_OUTPUTS,
    thrusters: Definitions.THRUSTERS_SIMULATION_OUTPUTS,
    pcm: Definitions.PCM_SIMULATION_OUTPUTS,
    pvt: Definitions.PVT_SIMULATION_OUTPUTS,
    adsorption: Definitions.ADSORPTION_SIMULATION_OUTPUTS,
    consumers: Definitions.CONSUMERS_SIMULATION_OUTPUTS,
    dc: Definitions.DC_SIMULATION_OUTPUTS,
    dhw: Definitions.DHW_SIMULATION_OUTPUTS,
    drives: Definitions.DRIVES_SIMULATION_OUTPUTS,
    thrs: Definitions.THRS_SIMULATION_OUTPUTS,
  },
);

export const SIMULATION_FIELDS: SimulationFields = {
  [SimulationComponentType.Pcs]: ["mode"],
  [SimulationComponentType.Temperature]: ["temperature"],
  [SimulationComponentType.OverpressureTemperature]: ["temperature", "overpressure"],
  [SimulationComponentType.Thruster]: ["heatFlow"],
  [SimulationComponentType.Boundary]: ["temperature", "flow"],
  [SimulationComponentType.HeatSource]: ["heatFlow"],
  [SimulationComponentType.ActiveHeatSource]: ["heatFlow"],
  [SimulationComponentType.Ugrid]: ["heatFlow"],
  [SimulationComponentType.PropulsionDrive]: ["heatFlow"],
  [SimulationComponentType.Flow]: ["flow"],
  [SimulationComponentType.HvacExchanger]: ["heatFlow", "maximumTemperature"],
  [SimulationComponentType.AdsorptionChiller]: ["freeCooling"],
};

export const SIMULATION_INPUT_QUERIES: Record<ThrsSimulationType, string> = {
  highTemperature: Queries.HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY,
  thrusters: Queries.THRUSTERS_SIMULATION_INPUTS_QUERY,
  pcm: Queries.PCM_SIMULATION_INPUTS_QUERY,
  pvt: Queries.PVT_SIMULATION_INPUTS_QUERY,
  adsorption: Queries.ADSORPTION_SIMULATION_INPUTS_QUERY,
  consumers: Queries.CONSUMERS_SIMULATION_INPUTS_QUERY,
  dc: Queries.DC_SIMULATION_INPUTS_QUERY,
  dhw: Queries.DHW_SIMULATION_INPUTS_QUERY,
  drives: Queries.DRIVES_SIMULATION_INPUTS_QUERY,
  thrs: Queries.THRS_SIMULATION_INPUTS_QUERY,
};

export const SIMULATION_OUTPUT_QUERIES: Record<ThrsSimulationType, string> = {
  highTemperature: Queries.HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY,
  thrusters: Queries.THRUSTERS_SIMULATION_OUTPUTS_QUERY,
  pcm: Queries.PCM_SIMULATION_OUTPUTS_QUERY,
  pvt: Queries.PVT_SIMULATION_OUTPUTS_QUERY,
  adsorption: Queries.ADSORPTION_SIMULATION_OUTPUTS_QUERY,
  consumers: Queries.CONSUMERS_SIMULATION_OUTPUTS_QUERY,
  dc: Queries.DC_SIMULATION_OUTPUTS_QUERY,
  dhw: Queries.DHW_SIMULATION_OUTPUTS_QUERY,
  drives: Queries.DRIVES_SIMULATION_OUTPUTS_QUERY,
  thrs: Queries.THRS_SIMULATION_OUTPUTS_QUERY,
};

const toInputType = <K extends string>(key: K): SimulationInputsType<K> =>
  `${key.charAt(0).toUpperCase()}${key.slice(1)}SimulationInputsType` as SimulationInputsType<K>;

const toOutputType = <K extends string>(key: K): SimulationOutputsType<K> =>
  `${key.charAt(0).toUpperCase()}${key.slice(1)}SimulationOutputsType` as SimulationOutputsType<K>;

const toUnionQueries = <K extends string, T extends Record<K, string>>(
  queries: T,
  keyMapFn: (key: string) => string,
): string =>
  Object.entries(queries)
    .map(([key, query]) => `... on ${keyMapFn(key)} { __typename ${query} }`)
    .join("\n");

export const QUERY_SIMULATION = gql`
  query QuerySimulation {
    simulation {
      inputs {
        ${toUnionQueries(SIMULATION_INPUT_QUERIES, toInputType)}
      }
      outputs {
        ${toUnionQueries(SIMULATION_OUTPUT_QUERIES, toOutputType)}
      }
    }
  }
`;
