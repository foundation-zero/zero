import {
  ControlComponentType,
  ControlFields,
  ControllerStateComponentType,
  ControllerStateFields,
  ModuleDefinition,
  SensorComponentType,
  SensorFields,
  SimulationComponentType,
  SimulationDefinitions,
  SimulationFields,
  ThrusterMode,
} from "@/modules/thrsim/types";
import { gql } from "@urql/vue";
import * as Definitions from "./consts.generated";
import {
  SimulationInputsType,
  SimulationOutputsType,
  ThrsQueries,
  ThrsSimulationType,
} from "./consts.types";
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
    sensorValues: Definitions.THRUSTERS_SENSOR_DEFINITION,
    controlValues: Definitions.THRUSTERS_CONTROL_DEFINITION,
    parameters: Definitions.THRUSTERS_PARAMETER_DEFINITION,
    controllerState: Definitions.THRUSTERS_CONTROLLER_STATE,
  },
  pcm: {
    sensorValues: Definitions.PCM_SENSOR_DEFINITION,
    controlValues: Definitions.PCM_CONTROL_DEFINITION,
    parameters: Definitions.PCM_PARAMETER_DEFINITION,
    controllerState: Definitions.PCM_CONTROLLER_STATE,
  },
  pvt: {
    sensorValues: Definitions.PVT_SENSOR_DEFINITION,
    controlValues: Definitions.PVT_CONTROL_DEFINITION,
    parameters: Definitions.PVT_PARAMETER_DEFINITION,
    controllerState: Definitions.PVT_CONTROLLER_STATE,
  },
  adsorption: {
    sensorValues: Definitions.ADSORPTION_SENSOR_DEFINITION,
    controlValues: Definitions.ADSORPTION_CONTROL_DEFINITION,
    parameters: Definitions.ADSORPTION_PARAMETER_DEFINITION,
    controllerState: Definitions.ADSORPTION_CONTROLLER_STATE,
  },
  consumers: {
    sensorValues: Definitions.CONSUMERS_SENSOR_DEFINITION,
    controlValues: Definitions.CONSUMERS_CONTROL_DEFINITION,
    parameters: Definitions.CONSUMERS_PARAMETER_DEFINITION,
    controllerState: Definitions.CONSUMERS_CONTROLLER_STATE,
  },
  dc: {
    sensorValues: Definitions.DC_SENSOR_DEFINITION,
    controlValues: Definitions.DC_CONTROL_DEFINITION,
    parameters: Definitions.DC_PARAMETER_DEFINITION,
    controllerState: Definitions.DC_CONTROLLER_STATE,
  },
  dhw: {
    sensorValues: Definitions.DHW_SENSOR_DEFINITION,
    controlValues: Definitions.DHW_CONTROL_DEFINITION,
    parameters: Definitions.DHW_PARAMETER_DEFINITION,
    controllerState: Definitions.DHW_CONTROLLER_STATE,
  },
  drives: {
    sensorValues: Definitions.DRIVES_SENSOR_DEFINITION,
    controlValues: Definitions.DRIVES_CONTROL_DEFINITION,
    parameters: Definitions.DRIVES_PARAMETER_DEFINITION,
    controllerState: Definitions.DRIVES_CONTROLLER_STATE,
  },
});

export type ThrsDefinitions = typeof DEFINITIONS;

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

export const CONTROL_FIELDS: ControlFields = {
  [ControlComponentType.Pump]: ["dutypoint", "on"],
  [ControlComponentType.Valve]: ["setpoint"],
  [ControlComponentType.Pcm]: ["on"],
  [ControlComponentType.Heatpump]: ["temperatureSetpoint", "on"],
};

export const CONTROLLER_STATE_FIELDS: ControllerStateFields = {
  [ControllerStateComponentType.DhwTanksController]: [
    "tank1State",
    "tank2State",
    "tank3State",
    "timeToFill",
  ],
  [ControllerStateComponentType.PIDController]: [
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
  [SensorComponentType.Flow]: ["flow", "temperature", "quantity"],
  [SensorComponentType.Pcm]: ["charged"],
  [SensorComponentType.Level]: ["level"],
  [SensorComponentType.LevelSwitch]: ["empty"],
};

export const SIMULATION_FIELDS: SimulationFields = {
  [SimulationComponentType.Pcs]: ["mode"],
  [SimulationComponentType.Temperature]: ["temperature"],
  [SimulationComponentType.OverpressureTemperature]: ["temperature", "overpressure"],
  [SimulationComponentType.Thruster]: ["active", "heatFlow"],
  [SimulationComponentType.Boundary]: ["temperature", "flow"],
  [SimulationComponentType.HeatSource]: ["heatFlow"],
  [SimulationComponentType.Flow]: ["flow"],
  [SimulationComponentType.HvacExchanger]: ["heatFlow", "maximumTemperature"],
};

export const toQueries = <
  TDefinitions extends ModuleDefinitions = typeof DEFINITIONS,
  Queries extends ThrsQueries<TDefinitions> = ThrsQueries<TDefinitions>,
>(
  input: Queries,
): Queries => input;

export const QUERIES = toQueries({
  thrusters: {
    controlValues: Queries.THRUSTERS_CONTROL_QUERY,
    parameters: Queries.THRUSTERS_PARAMETERS_QUERY,
    sensorValues: Queries.THRUSTERS_SENSOR_QUERY,
    controllerState: Queries.THRUSTERS_CONTROLLER_STATE_QUERY,
  },
  pcm: {
    controlValues: Queries.PCM_CONTROL_QUERY,
    parameters: Queries.PCM_PARAMETERS_QUERY,
    sensorValues: Queries.PCM_SENSOR_QUERY,
    controllerState: Queries.PCM_CONTROLLER_STATE_QUERY,
  },
  pvt: {
    controlValues: Queries.PVT_CONTROL_QUERY,
    parameters: Queries.PVT_PARAMETERS_QUERY,
    sensorValues: Queries.PVT_SENSOR_QUERY,
    controllerState: Queries.PVT_CONTROLLER_STATE_QUERY,
  },
  adsorption: {
    controlValues: Queries.ADSORPTION_CONTROL_QUERY,
    parameters: Queries.ADSORPTION_PARAMETERS_QUERY,
    sensorValues: Queries.ADSORPTION_SENSOR_QUERY,
    controllerState: Queries.ADSORPTION_CONTROLLER_STATE_QUERY,
  },
  consumers: {
    controlValues: Queries.CONSUMERS_CONTROL_QUERY,
    parameters: Queries.CONSUMERS_PARAMETERS_QUERY,
    sensorValues: Queries.CONSUMERS_SENSOR_QUERY,
    controllerState: Queries.CONSUMERS_CONTROLLER_STATE_QUERY,
  },
  dc: {
    controlValues: Queries.DC_CONTROL_QUERY,
    parameters: Queries.DC_PARAMETERS_QUERY,
    sensorValues: Queries.DC_SENSOR_QUERY,
    controllerState: Queries.DC_CONTROLLER_STATE_QUERY,
  },
  dhw: {
    controlValues: Queries.DHW_CONTROL_QUERY,
    parameters: Queries.DHW_PARAMETERS_QUERY,
    sensorValues: Queries.DHW_SENSOR_QUERY,
    controllerState: Queries.DHW_CONTROLLER_STATE_QUERY,
  },
  drives: {
    controlValues: Queries.DRIVES_CONTROL_QUERY,
    parameters: Queries.DRIVES_PARAMETERS_QUERY,
    sensorValues: Queries.DRIVES_SENSOR_QUERY,
    controllerState: Queries.DRIVES_CONTROLLER_STATE_QUERY,
  },
});

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
          ${Queries.THRUSTERS_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.THRUSTERS_CONTROL_QUERY}
        }
        parameters {
          ${Queries.THRUSTERS_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.THRUSTERS_CONTROLLER_STATE_QUERY}
        }
      }
      pcm {
        sensorValues {
          ${Queries.PCM_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.PCM_CONTROL_QUERY}
        }
        parameters {
          ${Queries.PCM_PARAMETERS_QUERY}
        }
        controllerState {
          Empty
        }
      }
      pvt {
        sensorValues {
          ${Queries.PVT_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.PVT_CONTROL_QUERY}
        }
        parameters {
          ${Queries.PVT_PARAMETERS_QUERY}
        }
        controllerState {
          Empty
        }
      }
      adsorption {
        sensorValues {
          ${Queries.ADSORPTION_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.ADSORPTION_CONTROL_QUERY}
        }
        parameters {
          ${Queries.ADSORPTION_PARAMETERS_QUERY}
        }
        controllerState {
          Empty
        }
      }
      consumers {
        sensorValues {
          ${Queries.CONSUMERS_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.CONSUMERS_CONTROL_QUERY}
        }
        parameters {
          ${Queries.CONSUMERS_PARAMETERS_QUERY}
        }
        controllerState {
          Empty
        }
      }
      dc {
        sensorValues {
          ${Queries.DC_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DC_CONTROL_QUERY}
        }
        parameters {
          ${Queries.DC_PARAMETERS_QUERY}
        }
        controllerState {
          Empty
        }
      }
      dhw {
        sensorValues {
          ${Queries.DHW_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DHW_CONTROL_QUERY}
        }
        parameters {
          ${Queries.DHW_PARAMETERS_QUERY}
        }
        controllerState {
          ${Queries.DHW_CONTROLLER_STATE_QUERY}
        }
      }
      drives {
        sensorValues {
          ${Queries.DRIVES_SENSOR_QUERY}
        }
        controlValues {
          ${Queries.DRIVES_CONTROL_QUERY}
        }
        parameters {
          ${Queries.DRIVES_PARAMETERS_QUERY}
        }
        controllerState {
          Empty
        }
      }
    }
  }
`;
