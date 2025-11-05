import {
  ControlComponentType,
  ControlDefinitions,
  ParameterDefinitions,
  ParametersType,
  SensorComponentType,
  SensorDefinitions,
  SimulationComponentType,
  SimulationDefinitions,
  ValveType,
} from "@/@types/thrs";

export const toControlDefinition = <T extends ControlDefinitions>(input: T): T => input;
export const toSensorDefinition = <T extends SensorDefinitions>(input: T): T => input;
export const toParameterDefinition = <T extends ParameterDefinitions>(input: T): T => input;
export const toSimulationDefinition = <T extends SimulationDefinitions>(input: T): T => input;

export const THRUSTERS_CONTROL_DEFINITION = toControlDefinition({
  thrustersPump1: {
    yardTag: "50001195",
    componentType: ControlComponentType.Pump,
  },
  thrustersPump2: {
    yardTag: "50001074",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersMixRecovery: {
    yardTag: "50001214-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersMixExchanger: {
    yardTag: "50001215",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  thrustersFlowcontrolAft: {
    yardTag: "50001064-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  thrustersFlowcontrolFwd: {
    yardTag: "50001066-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Shutoff,
  },
  thrustersShutoffRecovery: {
    yardTag: "50001091-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  thrustersSwitchAft: {
    yardTag: "50001091-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const THRUSTERS_SENSOR_DEFINITION = toSensorDefinition({
  thrustersPump1: {
    yardTag: "50001195",
    componentType: SensorComponentType.Pump,
  },
  thrustersPump2: {
    yardTag: "50001038-01",
    componentType: SensorComponentType.Pump,
  },
  thrustersTemperatureAftReturn: {
    yardTag: "50001038-02",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureFwdReturn: {
    yardTag: "50001038-28",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureSupply: {
    yardTag: "50001038-30",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureRecoveryMix: {
    yardTag: "50001074",
    componentType: SensorComponentType.Temperature,
    valveType: ValveType.Mix,
  },
  thrustersMixRecovery: {
    yardTag: "50001214-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersMixExchanger: {
    yardTag: "50001057-22",
    componentType: SensorComponentType.Valve,
  },
  thrustersFlowFwd: {
    yardTag: "50001057-23",
    componentType: SensorComponentType.Flow,
  },
  thrustersFlowAft: {
    yardTag: "50001215",
    componentType: SensorComponentType.Flow,
    valveType: ValveType.FlowControl,
  },
  thrustersFlowcontrolAft: {
    yardTag: "50001064-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  thrustersFlowcontrolFwd: {
    yardTag: "50001066-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Shutoff,
  },
  thrustersShutoffRecovery: {
    yardTag: "50001091-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  thrustersSwitchAft: {
    yardTag: "50001091-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  thrustersSwitchFwd: {
    yardTag: "50001093-01",
    componentType: SensorComponentType.Valve,
  },
  thrustersFlowRecovery: {
    yardTag: "50001097-01",
    componentType: SensorComponentType.Flow,
  },
  thrustersPressurePump: {
    yardTag: "50001097-02",
    componentType: SensorComponentType.Pressure,
  },
  thrustersPressureRelief: {
    yardTag: "15001001",
    componentType: SensorComponentType.Pressure,
  },
  thrustersAft: {
    yardTag: "15001002",
    componentType: SensorComponentType.Thruster,
  },
  thrustersFwd: {
    yardTag: "1500",
    componentType: SensorComponentType.Thruster,
  },
});

export const THRUSTERS_PARAMETER_DEFINITION = toParameterDefinition({
  maximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
  coolingTemperature: {
    componentType: ParametersType.Temperature,
  },
  coolingFlow: {
    componentType: ParametersType.Flow,
  },
  recoveryTemperature: {
    componentType: ParametersType.Temperature,
  },
  warmupTemperature: {
    componentType: ParametersType.Temperature,
  },
  thrustersMinimumFlow: {
    componentType: ParametersType.Flow,
  },
  thrustersMaximumFlow: {
    componentType: ParametersType.Flow,
  },
  pumpTuning: {
    componentType: ParametersType.Tuning,
  },
  warmupMixTuning: {
    componentType: ParametersType.Tuning,
  },
  heatDumpTuning: {
    componentType: ParametersType.Tuning,
  },
  aftFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  fwdFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  aftTemperatureTuning: {
    componentType: ParametersType.Tuning,
  },
  fwdTemperatureTuning: {
    componentType: ParametersType.Tuning,
  },
});

export const THRUSTERS_SIMULATION_INPUTS = toSimulationDefinition({
  thrustersAft: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersFwd: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersModuleSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  thrustersPcs: {
    componentType: SimulationComponentType.Pcs,
  },
});

export const THRUSTERS_SIMULATION_OUTPUTS = toSimulationDefinition({
  thrustersSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  thrustersModuleSupply: {
    componentType: SimulationComponentType.Flow,
  },
  thrustersModuleReturn: {
    componentType: SimulationComponentType.Boundary,
  },
});
