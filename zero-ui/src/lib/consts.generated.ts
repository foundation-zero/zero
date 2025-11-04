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

export const PCM_CONTROL_DEFINITION = toControlDefinition({
  pcmPump: {
    yardTag: "50001062-02",
    componentType: ControlComponentType.Valve,
  },
  pcmSwitchChargingReturn: {
    yardTag: "50001064-04",
    componentType: ControlComponentType.Valve,
  },
  pcmFlowcontrolModule1: {
    yardTag: "50001064-05",
    componentType: ControlComponentType.Valve,
  },
  pcmFlowcontrolModule2: {
    yardTag: "50001064-06",
    componentType: ControlComponentType.Valve,
  },
  pcmFlowcontrolModule3: {
    yardTag: "50001064-07",
    componentType: ControlComponentType.Valve,
  },
  pcmFlowcontrolModule4: {
    yardTag: "50001066-01",
    componentType: ControlComponentType.Valve,
  },
  pcmSwitchDischarging: {
    yardTag: "50001090-01",
    componentType: ControlComponentType.Valve,
  },
  pcmSwitchChargingSupply: {
    yardTag: "50001071-02",
    componentType: ControlComponentType.Valve,
  },
  pcmSwitchConsumers: {
    yardTag: "50001049",
    componentType: ControlComponentType.Valve,
  },
});

export const PVT_CONTROL_DEFINITION = toControlDefinition({
  pvtPumpMainFwd: {
    yardTag: "50001019",
    componentType: ControlComponentType.Valve,
  },
  pvtPumpMainAft: {
    yardTag: "50001021",
    componentType: ControlComponentType.Valve,
  },
  pvtPumpOwners: {
    yardTag: "50001044-01",
    componentType: ControlComponentType.Valve,
  },
  pvtMixMainFwd: {
    yardTag: "50001044-02",
    componentType: ControlComponentType.Valve,
  },
  pvtMixMainAft: {
    yardTag: "50001043-01",
    componentType: ControlComponentType.Valve,
  },
  pvtMixOwners: {
    yardTag: "50001067-01",
    componentType: ControlComponentType.Valve,
  },
  pvtSwitchMainFwd: {
    yardTag: "50001067-02",
    componentType: ControlComponentType.Valve,
  },
  pvtSwitchMainAft: {
    yardTag: "50001069-01",
    componentType: ControlComponentType.Valve,
  },
  pvtSwitchOwners: {
    yardTag: "50001047-02",
    componentType: ControlComponentType.Valve,
  },
});

export const PVT_SENSOR_DEFINITION = toSensorDefinition({
  pvtPumpMainFwd: {
    yardTag: "50001019",
    componentType: SensorComponentType.Pump,
  },
  pvtPumpMainAft: {
    yardTag: "50001021",
    componentType: SensorComponentType.Pump,
  },
  pvtPumpOwners: {
    yardTag: "50001038-03",
    componentType: SensorComponentType.Pump,
  },
  pvtTemperatureMainFwdReturn: {
    yardTag: "50001038-23",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainFwdSupply: {
    yardTag: "50001038-73",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainAftReturn: {
    yardTag: "50001038-22",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainAftSupply: {
    yardTag: "50001038-21",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersSupply: {
    yardTag: "50001038-04",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersReturn: {
    yardTag: "50001044-01",
    componentType: SensorComponentType.Temperature,
  },
  pvtMixMainFwd: {
    yardTag: "50001044-02",
    componentType: SensorComponentType.Valve,
  },
  pvtMixMainAft: {
    yardTag: "50001043-01",
    componentType: SensorComponentType.Valve,
  },
  pvtMixOwners: {
    yardTag: "50001058-12",
    componentType: SensorComponentType.Valve,
  },
  pvtFlowMainFwdRecovery: {
    yardTag: "50001058-13",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainAftRecovery: {
    yardTag: "50001057-03",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersRecovery: {
    yardTag: "50001097-03",
    componentType: SensorComponentType.Flow,
  },
  pvtPressureMainFwd: {
    yardTag: "50001097-04",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureMainAft: {
    yardTag: "50001097-05",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureOwners: {
    yardTag: "50001067-01",
    componentType: SensorComponentType.Pressure,
  },
  pvtSwitchMainFwd: {
    yardTag: "50001067-02",
    componentType: SensorComponentType.Valve,
  },
  pvtSwitchMainAft: {
    yardTag: "50001069-01",
    componentType: SensorComponentType.Valve,
  },
  pvtSwitchOwners: {
    yardTag: "50001047-02",
    componentType: SensorComponentType.Valve,
  },
  pvtMixExchanger: {
    yardTag: "50001038-24",
    componentType: SensorComponentType.Valve,
  },
  pvtTemperatureSupply: {
    yardTag: "50009005-01",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString11Return: {
    yardTag: "50009005-19",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString12Return: {
    yardTag: "50009005-03",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString21Return: {
    yardTag: "50009005-04",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString22Return: {
    yardTag: "50009005-05",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString3Return: {
    yardTag: "50009005-06",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString4Return: {
    yardTag: "50009005-07",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString51Return: {
    yardTag: "50009005-08",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString52Return: {
    yardTag: "50009005-09",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString61Return: {
    yardTag: "50009005-10",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString62Return: {
    yardTag: "50009006-01",
    componentType: SensorComponentType.Temperature,
  },
  pvtFlowMainString11: {
    yardTag: "50009009-05",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString12: {
    yardTag: "50009006-03",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString21: {
    yardTag: "50009006-04",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString22: {
    yardTag: "50009009-01",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString3: {
    yardTag: "50009009-02",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString4: {
    yardTag: "50009006-05",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString51: {
    yardTag: "50009006-06",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString52: {
    yardTag: "50009006-07",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString61: {
    yardTag: "50009006-08",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString62: {
    yardTag: "50009005-26",
    componentType: SensorComponentType.Flow,
  },
  pvtTemperatureMainString1Supply: {
    yardTag: "50009005-25",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString2Supply: {
    yardTag: "50009005-24",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString3Supply: {
    yardTag: "50009005-23",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString4Supply: {
    yardTag: "50009005-22",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString5Supply: {
    yardTag: "50009005-21",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString6Supply: {
    yardTag: "50009005-11",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString71Return: {
    yardTag: "50009005-12",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString72Return: {
    yardTag: "50009005-13",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString81Return: {
    yardTag: "50009005-14",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString82Return: {
    yardTag: "50009005-15",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString9Return: {
    yardTag: "50009005-16",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString10Return: {
    yardTag: "50009005-17",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString111Return: {
    yardTag: "50009005-18",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString112Return: {
    yardTag: "50009005-20",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString13Return: {
    yardTag: "50009006-09",
    componentType: SensorComponentType.Temperature,
  },
  pvtFlowMainString71: {
    yardTag: "50009006-10",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString72: {
    yardTag: "50009006-11",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString81: {
    yardTag: "50009006-12",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString82: {
    yardTag: "50009009-03",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString9: {
    yardTag: "50009009-04",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString10: {
    yardTag: "50009006-13",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString111: {
    yardTag: "50009006-14",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString112: {
    yardTag: "50009009-06",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString13: {
    yardTag: "50009005-27",
    componentType: SensorComponentType.Flow,
  },
  pvtTemperatureMainString7Supply: {
    yardTag: "50009005-28",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString8Supply: {
    yardTag: "50009005-29",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString9Supply: {
    yardTag: "50009005-30",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString10Supply: {
    yardTag: "50009005-31",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString11Supply: {
    yardTag: "50009005-32",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString12Supply: {
    yardTag: "50009005-33",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString13Supply: {
    yardTag: "50009005-34",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString1Return: {
    yardTag: "50009005-35",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString2Return: {
    yardTag: "50009005-36",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString3Return: {
    yardTag: "50009005-37",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString4Return: {
    yardTag: "50009005-38",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString5Return: {
    yardTag: "50009005-39",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString6Return: {
    yardTag: "50009009-07",
    componentType: SensorComponentType.Temperature,
  },
  pvtFlowOwnersString1: {
    yardTag: "50009009-08",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString2: {
    yardTag: "50009009-09",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString3: {
    yardTag: "50009009-10",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString4: {
    yardTag: "50009009-11",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString5: {
    yardTag: "50009009-12",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString6: {
    yardTag: "50009005-40",
    componentType: SensorComponentType.Flow,
  },
  pvtTemperatureOwnersString1Supply: {
    yardTag: "50009005-41",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString2Supply: {
    yardTag: "50009005-42",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString3Supply: {
    yardTag: "50009005-43",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString4Supply: {
    yardTag: "50009005-44",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString5Supply: {
    yardTag: "50009005-45",
    componentType: SensorComponentType.Temperature,
  },
});

export const PVT_PARAMETER_DEFINITION = toParameterDefinition({
  maximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
  recoveryTemperature: {
    componentType: ParametersType.Temperature,
  },
  warmupTemperature: {
    componentType: ParametersType.Temperature,
  },
  recoveryActivationStringTemperature: {
    componentType: ParametersType.Temperature,
  },
  minimumReturnTemperature: {
    componentType: ParametersType.Temperature,
  },
  mainFwdMinimumPumpDutypoint: {
    componentType: ParametersType.Temperature,
  },
  mainAftMinimumPumpDutypoint: {
    componentType: ParametersType.Temperature,
  },
  ownersMinimumPumpDutypoint: {
    componentType: ParametersType.Temperature,
  },
  heatDumpTuning: {
    componentType: ParametersType.Tuning,
  },
  mainFwdMixTuning: {
    componentType: ParametersType.Tuning,
  },
  mainAftMixTuning: {
    componentType: ParametersType.Tuning,
  },
  ownersMixTuning: {
    componentType: ParametersType.Tuning,
  },
  mainFwdPumpTuning: {
    componentType: ParametersType.Tuning,
  },
  mainAftPumpTuning: {
    componentType: ParametersType.Tuning,
  },
  ownersPumpTuning: {
    componentType: ParametersType.Tuning,
  },
});

export const PVT_SIMULATION_INPUTS = toSimulationDefinition({
  pvtModuleSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  pvtSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const PVT_SIMULATION_OUTPUTS = toSimulationDefinition({
  pvtModuleReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtModuleSupply: {
    componentType: SimulationComponentType.Flow,
  },
  pvtSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});

export const PCM_SENSOR_DEFINITION = toSensorDefinition({
  pcmPump: {
    yardTag: "50001038-31",
    componentType: SensorComponentType.Pump,
  },
  pcmTemperatureProducersReturn: {
    yardTag: "50001038-55",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureProducersSupply: {
    yardTag: "50001038-32",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule1Out: {
    yardTag: "50001038-33",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule2Out: {
    yardTag: "50001038-34",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule3Out: {
    yardTag: "50001038-35",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule4Out: {
    yardTag: "50001049",
    componentType: SensorComponentType.Temperature,
  },
  pcmModule1: {
    yardTag: "50001050",
  },
  pcmModule2: {
    yardTag: "50001051",
  },
  pcmModule3: {
    yardTag: "50001052",
  },
  pcmModule4: {
    yardTag: "50001057-18",
  },
  pcmFlowModule1: {
    yardTag: "50001057-19",
    componentType: SensorComponentType.Flow,
  },
  pcmFlowModule2: {
    yardTag: "50001057-20",
    componentType: SensorComponentType.Flow,
  },
  pcmFlowModule3: {
    yardTag: "50001057-21",
    componentType: SensorComponentType.Flow,
  },
  pcmFlowModule4: {
    yardTag: "50001062-02",
    componentType: SensorComponentType.Flow,
  },
  pcmSwitchChargingReturn: {
    yardTag: "50001064-04",
    componentType: SensorComponentType.Valve,
  },
  pcmFlowcontrolModule1: {
    yardTag: "50001064-05",
    componentType: SensorComponentType.Valve,
  },
  pcmFlowcontrolModule2: {
    yardTag: "50001064-06",
    componentType: SensorComponentType.Valve,
  },
  pcmFlowcontrolModule3: {
    yardTag: "50001064-07",
    componentType: SensorComponentType.Valve,
  },
  pcmFlowcontrolModule4: {
    yardTag: "50001066-01",
    componentType: SensorComponentType.Valve,
  },
  pcmSwitchDischarging: {
    yardTag: "50001090-01",
    componentType: SensorComponentType.Valve,
  },
  pcmSwitchChargingSupply: {
    yardTag: "50001071-02",
    componentType: SensorComponentType.Valve,
  },
});

export const PCM_PARAMETER_DEFINITION = toParameterDefinition({
  pcmDischargeFlow: {
    componentType: ParametersType.Flow,
  },
  pcmChargeFlow: {
    componentType: ParametersType.Flow,
  },
  minimumChargingDt: {
    componentType: ParametersType.Temperature,
  },
  minimumChargingTemperature: {
    componentType: ParametersType.Temperature,
  },
  pumpTuning: {
    componentType: ParametersType.Tuning,
  },
  module1FlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  module2FlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  module3FlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  module4FlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
});

export const PCM_SIMULATION_INPUTS = toSimulationDefinition({
  pcmProducersSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmConsumersSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  pcmFreshwaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const PCM_SIMULATION_OUTPUTS = toSimulationDefinition({
  pcmConsumersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmProducersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmFreshwaterReturn: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const CONSUMERS_CONTROL_DEFINITION = toControlDefinition({
  consumersSwitchFahrenheitDirectSupply: {
    yardTag: "50001061",
    componentType: ControlComponentType.Valve,
  },
  consumersFlowcontrolFahrenheit: {
    yardTag: "50001062-01",
    componentType: ControlComponentType.Valve,
  },
  consumersFlowcontrolBypass: {
    yardTag: "50001065-01",
    componentType: ControlComponentType.Valve,
  },
  consumersFlowcontrolBoosting: {
    yardTag: "50001066-02",
    componentType: ControlComponentType.Valve,
  },
  consumersSwitchFahrenheitExchanger: {
    yardTag: "50001066-03",
    componentType: ControlComponentType.Valve,
  },
  consumersSwitchFahrenheitDirectReturn: {
    yardTag: "50001067-15",
    componentType: ControlComponentType.Valve,
  },
});

export const CONSUMERS_SENSOR_DEFINITION = toSensorDefinition({
  consumersSwitchFahrenheitDirectSupply: {
    yardTag: "50001038-48",
    componentType: SensorComponentType.Valve,
  },
  consumersTemperatureBoostingReturn: {
    yardTag: "50001038-49",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureFahrenheitReturn: {
    yardTag: "50001038-53",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureBoostingSupply: {
    yardTag: "50001038-54",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureFahrenheitSupply: {
    yardTag: "50001058-07",
    componentType: SensorComponentType.Temperature,
  },
  consumersFlowBoosting: {
    yardTag: "50001058-08",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowFahrenheit: {
    yardTag: "50001060-01",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowBypass: {
    yardTag: "50001061",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowcontrolFahrenheit: {
    yardTag: "50001062-01",
    componentType: SensorComponentType.Valve,
  },
  consumersFlowcontrolBypass: {
    yardTag: "50001065-01",
    componentType: SensorComponentType.Valve,
  },
  consumersFlowcontrolBoosting: {
    yardTag: "50001066-02",
    componentType: SensorComponentType.Valve,
  },
  consumersSwitchFahrenheitExchanger: {
    yardTag: "50001066-03",
    componentType: SensorComponentType.Valve,
  },
  consumersSwitchFahrenheitDirectReturn: {
    yardTag: "50001067-15",
    componentType: SensorComponentType.Valve,
  },
});

export const CONSUMERS_PARAMETER_DEFINITION = toParameterDefinition({
  boostingFlowRatioSetpoint: {
    componentType: ParametersType.Temperature,
  },
  fahrenheitFlowRatioSetpoint: {
    componentType: ParametersType.Temperature,
  },
  boostingFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  bypassFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  fahrenheitFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
});

export const CONSUMERS_SIMULATION_INPUTS = toSimulationDefinition({
  consumersFahrenheitSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersModuleSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersBoostingSupply: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const CONSUMERS_SIMULATION_OUTPUTS = toSimulationDefinition({
  consumersFahrenheitReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersBoostingReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersModuleReturn: {
    componentType: SimulationComponentType.Boundary,
  },
});
