import {
  ControlComponentType,
  ControlFields,
  ModuleDefinition,
  SensorComponentType,
  SensorFields,
  SimulationComponentType,
  SimulationFields,
} from "@/@types/thrs";
import {
  THRUSTERS_CONTROL_DEFINITION,
  THRUSTERS_PARAMETER_DEFINITION,
  THRUSTERS_SENSOR_DEFINITION,
  THRUSTERS_SIMULATION_INPUTS,
  THRUSTERS_SIMULATION_OUTPUTS,
} from "./consts.generated";
import { THRSQueries } from "./consts.types";
import {
  THRUSTERS_CONTROL_QUERY,
  THRUSTERS_PARAMETERS_QUERY,
  THRUSTERS_SENSOR_QUERY,
  THRUSTERS_SIMULATION_INPUTS_QUERY,
  THRUSTERS_SIMULATION_OUTPUTS_QUERY,
} from "./queries.generated";

export * from "./consts.types";

export const CO2_THRESHOLDS: [warning: number, critical: number] = [1000, 2000];
export const CO2_RANGE = [400, 2500];
export const CO2_SETPOINT_RANGE = [400, 1000];

export const HUMIDITY_THRESHOLDS: [humidityLow: number, humidityHigh: number] = [35, 60];
export const HUMIDITY_RANGE = [30, 80];
export const HUMIDITY_SETPOINT_RANGE = [40, 60];

export const TEMPERATURE_THRESHOLDS: [tempWarm: number, tempHot: number] = [25, 30];
export const TEMPERATURE_RANGE = [15, 35];
export const TEMPERATURE_SETPOINT_RANGE = [18, 23];

export const DEMO_MODE = import.meta?.env?.VITE_DEMO_MODE === "1";

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
});

export const CONTROL_FIELDS: ControlFields = {
  [ControlComponentType.Pump]: ["dutypoint", "on"],
  [ControlComponentType.Valve]: ["setpoint"],
};

export const SENSOR_FIELDS: SensorFields = {
  [SensorComponentType.Pump]: ["flow", "speed", "opTime"],
  [SensorComponentType.Valve]: ["positionRel"],
  [SensorComponentType.Pressure]: ["pressure"],
  [SensorComponentType.Temperature]: ["temperature"],
  [SensorComponentType.Thruster]: ["active"],
  [SensorComponentType.Pcs]: ["mode"],
  [SensorComponentType.Flow]: ["flow", "temperature"],
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
});
