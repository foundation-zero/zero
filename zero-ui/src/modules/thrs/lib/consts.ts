import {
  ControlComponentType,
  ControlFields,
  ModuleDefinition,
  SensorComponentType,
  SensorFields,
  SimulationComponentType,
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
import { THRSQueries } from "./consts.types";
import {
  CONSUMERS_CONTROL_QUERY,
  CONSUMERS_PARAMETERS_QUERY,
  CONSUMERS_SENSOR_QUERY,
  CONSUMERS_SIMULATION_INPUTS_QUERY,
  CONSUMERS_SIMULATION_OUTPUTS_QUERY,
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

export const toDefinitions = <T extends Record<string, ModuleDefinition>>(input: T): T => input;

export const DEFINITIONS = toDefinitions({
  thrusters: {
    sensorValues: THRUSTERS_SENSOR_DEFINITION,
    controlValues: THRUSTERS_CONTROL_DEFINITION,
    parameters: THRUSTERS_PARAMETER_DEFINITION,
    simulation: {
      inputs: THRUSTERS_SIMULATION_INPUTS,
      outputs: THRUSTERS_SIMULATION_OUTPUTS,
    },
  },
  pcm: {
    sensorValues: PCM_SENSOR_DEFINITION,
    controlValues: PCM_CONTROL_DEFINITION,
    parameters: PCM_PARAMETER_DEFINITION,
    simulation: {
      inputs: PCM_SIMULATION_INPUTS,
      outputs: PCM_SIMULATION_OUTPUTS,
    },
  },
  pvt: {
    sensorValues: PVT_SENSOR_DEFINITION,
    controlValues: PVT_CONTROL_DEFINITION,
    parameters: PVT_PARAMETER_DEFINITION,
    simulation: {
      inputs: PVT_SIMULATION_INPUTS,
      outputs: PVT_SIMULATION_OUTPUTS,
    },
  },
  consumers: {
    sensorValues: CONSUMERS_SENSOR_DEFINITION,
    controlValues: CONSUMERS_CONTROL_DEFINITION,
    parameters: CONSUMERS_PARAMETER_DEFINITION,
    simulation: {
      inputs: CONSUMERS_SIMULATION_INPUTS,
      outputs: CONSUMERS_SIMULATION_OUTPUTS,
    },
  },
});

export const CONTROL_FIELDS: ControlFields = {
  [ControlComponentType.Pump]: ["dutypoint", "on"],
  [ControlComponentType.Valve]: ["setpoint"],
  [ControlComponentType.Pcm]: ["on"],
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
};

export const SIMULATION_FIELDS: SimulationFields = {
  [SimulationComponentType.Pcs]: ["mode"],
  [SimulationComponentType.Temperature]: ["temperature"],
  [SimulationComponentType.Thruster]: ["active", "heatFlow"],
  [SimulationComponentType.Boundary]: ["temperature", "flow"],
};

export const toQueries = <
  TDefinitions extends Record<string, ModuleDefinition> = typeof DEFINITIONS,
  Queries extends THRSQueries<TDefinitions> = THRSQueries<TDefinitions>,
>(
  input: Queries,
): Queries => input;

export const QUERIES = toQueries({
  thrusters: {
    controlValues: THRUSTERS_CONTROL_QUERY,
    parameters: THRUSTERS_PARAMETERS_QUERY,
    sensorValues: THRUSTERS_SENSOR_QUERY,
    simulation: {
      inputs: THRUSTERS_SIMULATION_INPUTS_QUERY,
      outputs: THRUSTERS_SIMULATION_OUTPUTS_QUERY,
    },
  },
  pcm: {
    controlValues: PCM_CONTROL_QUERY,
    parameters: PCM_PARAMETERS_QUERY,
    sensorValues: PCM_SENSOR_QUERY,
    simulation: {
      inputs: PCM_SIMULATION_INPUTS_QUERY,
      outputs: PCM_SIMULATION_OUTPUTS_QUERY,
    },
  },
  pvt: {
    controlValues: PVT_CONTROL_QUERY,
    parameters: PVT_PARAMETERS_QUERY,
    sensorValues: PVT_SENSOR_QUERY,
    simulation: {
      inputs: PVT_SIMULATION_INPUTS_QUERY,
      outputs: PVT_SIMULATION_OUTPUTS_QUERY,
    },
  },
  consumers: {
    controlValues: CONSUMERS_CONTROL_QUERY,
    parameters: CONSUMERS_PARAMETERS_QUERY,
    sensorValues: CONSUMERS_SENSOR_QUERY,
    simulation: {
      inputs: CONSUMERS_SIMULATION_INPUTS_QUERY,
      outputs: CONSUMERS_SIMULATION_OUTPUTS_QUERY,
    },
  },
});

export const QUERY_ALL = gql`
  query QueryAll {
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
        simulation {
          inputs {
            ${THRUSTERS_SIMULATION_INPUTS_QUERY}
          }
          outputs {
            ${THRUSTERS_SIMULATION_OUTPUTS_QUERY}
          }
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
        simulation {
          inputs {
            ${PCM_SIMULATION_INPUTS_QUERY}
          }
          outputs {
            ${PCM_SIMULATION_OUTPUTS_QUERY}
          }
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
        simulation {
          inputs {
            ${PVT_SIMULATION_INPUTS_QUERY}
          }
          outputs {
            ${PVT_SIMULATION_OUTPUTS_QUERY}
          }
        }
      }
      
    }
  }
`;
