import { ThrusterMode } from "@/modules/thrapp/types/thrs";
import { gql } from "@urql/vue";
import { SimulationComponentType, SimulationDefinitions, SimulationFields } from "../types";
import { ThrsSimulationType } from "./consts.types";
import * as Definitions from "./simulation.consts";

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
  [SimulationComponentType.AmcsMode]: ["mode"],
};

// Each component with the fields of its type, the timestamp named as thrsim reads it.
const selection = (definitions: SimulationDefinitions): string =>
  Object.entries(definitions)
    .map(
      ([component, { componentType }]) =>
        `${component} { ${SIMULATION_FIELDS[componentType]
          .map((field) => `${field} { value timestamp: timeStamp }`)
          .join(" ")} }`,
    )
    .join("\n");

// The simulator on the MQTT GraphQL API. It has one inputs and one outputs type, the whole
// THRS simulation's, which every simulation type publishes a part of; the status says which
// type runs. Only a simulator in lockstep publishes a status.
// TODO: generate from the thrs-control Spec, like thrapp's definitions; for now from thrsim's
// own definitions of the THRS simulation.
export const SIMULATOR_QUERY = gql`
  query Simulator {
    thrs {
      simulator {
        status { status mode simulationTime }
        simulationInputs {
          ${selection(SIMULATION.inputs.thrs)}
        }
        simulationOutputs {
          ${selection(SIMULATION.outputs.thrs)}
        }
      }
    }
  }
`;
