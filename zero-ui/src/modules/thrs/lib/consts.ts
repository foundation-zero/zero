import {
  ControlComponentType,
  ControlFields,
  ModuleDefinition,
  SensorComponentType,
  SensorFields,
  SimulationComponentType,
  SimulationDefinitions,
  SimulationFields,
  ThrusterMode,
} from "@/modules/thrs/types";
import { gql } from "@urql/vue";
import {
  CONSUMERS_CONTROL_DEFINITION,
  CONSUMERS_PARAMETER_DEFINITION,
  CONSUMERS_SENSOR_DEFINITION,
  CONSUMERS_SIMULATION_INPUTS,
  CONSUMERS_SIMULATION_OUTPUTS,
  DHW_CONTROL_DEFINITION,
  DHW_PARAMETER_DEFINITION,
  DHW_SENSOR_DEFINITION,
  DHW_SIMULATION_INPUTS,
  DHW_SIMULATION_OUTPUTS,
  HIGH_TEMPERATURE_SIMULATION_INPUTS,
  HIGH_TEMPERATURE_SIMULATION_OUTPUTS,
  PCM_CONTROL_DEFINITION,
  PCM_PARAMETER_DEFINITION,
  PCM_SENSOR_DEFINITION,
  PCM_SIMULATION_INPUTS,
  PCM_SIMULATION_OUTPUTS,
  PVT_CONTROL_DEFINITION,
  PVT_PARAMETER_DEFINITION,
  PVT_SENSOR_DEFINITION,
  PVT_SIMULATION_INPUTS,
  PVT_SIMULATION_OUTPUTS,
  THRUSTERS_CONTROL_DEFINITION,
  THRUSTERS_PARAMETER_DEFINITION,
  THRUSTERS_SENSOR_DEFINITION,
  THRUSTERS_SIMULATION_INPUTS,
  THRUSTERS_SIMULATION_OUTPUTS,
} from "./consts.generated";
import {
  SimulationInputsType,
  SimulationOutputsType,
  ThrsQueries,
  ThrsSimulationType,
} from "./consts.types";
import {
  CONSUMERS_CONTROL_QUERY,
  CONSUMERS_PARAMETERS_QUERY,
  CONSUMERS_SENSOR_QUERY,
  CONSUMERS_SIMULATION_INPUTS_QUERY,
  CONSUMERS_SIMULATION_OUTPUTS_QUERY,
  DHW_CONTROL_QUERY,
  DHW_PARAMETERS_QUERY,
  DHW_SENSOR_QUERY,
  DHW_SIMULATION_INPUTS_QUERY,
  DHW_SIMULATION_OUTPUTS_QUERY,
  HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY,
  HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY,
  PCM_CONTROL_QUERY,
  PCM_PARAMETERS_QUERY,
  PCM_SENSOR_QUERY,
  PCM_SIMULATION_INPUTS_QUERY,
  PCM_SIMULATION_OUTPUTS_QUERY,
  PVT_CONTROL_QUERY,
  PVT_PARAMETERS_QUERY,
  PVT_SENSOR_QUERY,
  PVT_SIMULATION_INPUTS_QUERY,
  PVT_SIMULATION_OUTPUTS_QUERY,
  THRUSTERS_CONTROL_QUERY,
  THRUSTERS_PARAMETERS_QUERY,
  THRUSTERS_SENSOR_QUERY,
  THRUSTERS_SIMULATION_INPUTS_QUERY,
  THRUSTERS_SIMULATION_OUTPUTS_QUERY,
} from "./queries.generated";

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

type ModuleDefinitions = Record<string, ModuleDefinition>;

export const toDefinitions = <T extends ModuleDefinitions>(input: T): T => input;

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

export const DEFINITIONS = toDefinitions({
  thrusters: {
    sensorValues: THRUSTERS_SENSOR_DEFINITION,
    controlValues: THRUSTERS_CONTROL_DEFINITION,
    parameters: THRUSTERS_PARAMETER_DEFINITION,
  },
  pcm: {
    sensorValues: PCM_SENSOR_DEFINITION,
    controlValues: PCM_CONTROL_DEFINITION,
    parameters: PCM_PARAMETER_DEFINITION,
  },
  pvt: {
    sensorValues: PVT_SENSOR_DEFINITION,
    controlValues: PVT_CONTROL_DEFINITION,
    parameters: PVT_PARAMETER_DEFINITION,
  },
  consumers: {
    sensorValues: CONSUMERS_SENSOR_DEFINITION,
    controlValues: CONSUMERS_CONTROL_DEFINITION,
    parameters: CONSUMERS_PARAMETER_DEFINITION,
  },
  dhw: {
    sensorValues: DHW_SENSOR_DEFINITION,
    controlValues: DHW_CONTROL_DEFINITION,
    parameters: DHW_PARAMETER_DEFINITION,
  },
});

export type ThrsDefinitions = typeof DEFINITIONS;

export const SIMULATION = toSimulation(
  {
    highTemperature: HIGH_TEMPERATURE_SIMULATION_INPUTS,
    thrusters: THRUSTERS_SIMULATION_INPUTS,
    pcm: PCM_SIMULATION_INPUTS,
    pvt: PVT_SIMULATION_INPUTS,
    consumers: CONSUMERS_SIMULATION_INPUTS,
    dhw: DHW_SIMULATION_INPUTS,
  },
  {
    highTemperature: HIGH_TEMPERATURE_SIMULATION_OUTPUTS,
    thrusters: THRUSTERS_SIMULATION_OUTPUTS,
    pcm: PCM_SIMULATION_OUTPUTS,
    pvt: PVT_SIMULATION_OUTPUTS,
    consumers: CONSUMERS_SIMULATION_OUTPUTS,
    dhw: DHW_SIMULATION_OUTPUTS,
  },
);

export const CONTROL_FIELDS: ControlFields = {
  [ControlComponentType.Pump]: ["dutypoint", "on"],
  [ControlComponentType.Valve]: ["setpoint"],
  [ControlComponentType.Pcm]: ["on"],
  [ControlComponentType.Heatpump]: ["dutypoint", "on"],
  [ControlComponentType.DhwTanksController]: [
    "tank1State",
    "tank2State",
    "tank3State",
    "timeToFill",
  ],
  [ControlComponentType.PIDController]: [
    "setpoint",
    "measurement",
    "output",
    "error",
    "enabled",
    "tuning",
    "components",
  ],
};

export const SENSOR_FIELDS: SensorFields = {
  [SensorComponentType.Pump]: ["flow", "speed", "opTime"],
  [SensorComponentType.Valve]: ["positionRel"],
  [SensorComponentType.Pressure]: ["pressure"],
  [SensorComponentType.Temperature]: ["temperature"],
  [SensorComponentType.Thruster]: ["active"],
  [SensorComponentType.Pcs]: ["mode"],
  [SensorComponentType.Flow]: ["flow", "temperature"],
  [SensorComponentType.Pcm]: ["charged"],
  [SensorComponentType.Level]: ["level"],
};

export const SIMULATION_FIELDS: SimulationFields = {
  [SimulationComponentType.Pcs]: ["mode"],
  [SimulationComponentType.Temperature]: ["temperature"],
  [SimulationComponentType.OverpressureTemperature]: ["temperature", "overpressure"],
  [SimulationComponentType.Thruster]: ["active", "heatFlow"],
  [SimulationComponentType.Boundary]: ["temperature", "flow"],
  [SimulationComponentType.HeatSource]: ["heatFlow"],
};

export const toQueries = <
  TDefinitions extends ModuleDefinitions = typeof DEFINITIONS,
  Queries extends ThrsQueries<TDefinitions> = ThrsQueries<TDefinitions>,
>(
  input: Queries,
): Queries => input;

export const QUERIES = toQueries({
  thrusters: {
    controlValues: THRUSTERS_CONTROL_QUERY,
    parameters: THRUSTERS_PARAMETERS_QUERY,
    sensorValues: THRUSTERS_SENSOR_QUERY,
  },
  pcm: {
    controlValues: PCM_CONTROL_QUERY,
    parameters: PCM_PARAMETERS_QUERY,
    sensorValues: PCM_SENSOR_QUERY,
  },
  pvt: {
    controlValues: PVT_CONTROL_QUERY,
    parameters: PVT_PARAMETERS_QUERY,
    sensorValues: PVT_SENSOR_QUERY,
  },
  consumers: {
    controlValues: CONSUMERS_CONTROL_QUERY,
    parameters: CONSUMERS_PARAMETERS_QUERY,
    sensorValues: CONSUMERS_SENSOR_QUERY,
  },
  dhw: {
    controlValues: DHW_CONTROL_QUERY,
    parameters: DHW_PARAMETERS_QUERY,
    sensorValues: DHW_SENSOR_QUERY,
  },
});

export const SIMULATION_INPUT_QUERIES: Record<ThrsSimulationType, string> = {
  highTemperature: HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY,
  thrusters: THRUSTERS_SIMULATION_INPUTS_QUERY,
  pcm: PCM_SIMULATION_INPUTS_QUERY,
  pvt: PVT_SIMULATION_INPUTS_QUERY,
  consumers: CONSUMERS_SIMULATION_INPUTS_QUERY,
  dhw: DHW_SIMULATION_INPUTS_QUERY,
};

export const SIMULATION_OUTPUT_QUERIES: Record<ThrsSimulationType, string> = {
  highTemperature: HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY,
  thrusters: THRUSTERS_SIMULATION_OUTPUTS_QUERY,
  pcm: PCM_SIMULATION_OUTPUTS_QUERY,
  pvt: PVT_SIMULATION_OUTPUTS_QUERY,
  consumers: CONSUMERS_SIMULATION_OUTPUTS_QUERY,
  dhw: DHW_SIMULATION_OUTPUTS_QUERY,
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

export const QUERY_ALL = gql`
  query QueryAll {
    simulation {
      inputs {
        ${toUnionQueries(SIMULATION_INPUT_QUERIES, toInputType)}
      }
      outputs {
        ${toUnionQueries(SIMULATION_OUTPUT_QUERIES, toOutputType)}
      }
    }
    modules {
      thrusters {
        sensorValues {
          ${THRUSTERS_SENSOR_QUERY}
        }
        controlValues {
          ${THRUSTERS_CONTROL_QUERY}
        }
        parameters {
          ${THRUSTERS_PARAMETERS_QUERY}
        }
      }
      pcm {
        sensorValues {
          ${PCM_SENSOR_QUERY}
        }
        controlValues {
          ${PCM_CONTROL_QUERY}
        }
        parameters {
          ${PCM_PARAMETERS_QUERY}
        }
      }
      pvt {
        sensorValues {
          ${PVT_SENSOR_QUERY}
        }
        controlValues {
          ${PVT_CONTROL_QUERY}
        }
        parameters {
          ${PVT_PARAMETERS_QUERY}
        }
      }
      consumers {
        sensorValues {
          ${CONSUMERS_SENSOR_QUERY}
        }
        controlValues {
          ${CONSUMERS_CONTROL_QUERY}
        }
        parameters {
          ${CONSUMERS_PARAMETERS_QUERY}
        }
      }
      dhw {
        sensorValues {
          ${DHW_SENSOR_QUERY}
        }
        controlValues {
          ${DHW_CONTROL_QUERY}
        }
        parameters {
          ${DHW_PARAMETERS_QUERY}
        }
      }
    }
  }
`;
