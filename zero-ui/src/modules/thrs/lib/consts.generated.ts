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
} from "@/modules/thrs/types";

export const toControlDefinition = <T extends ControlDefinitions>(input: T): T => input;
export const toSensorDefinition = <T extends SensorDefinitions>(input: T): T => input;
export const toParameterDefinition = <T extends ParameterDefinitions>(input: T): T => input;
export const toSimulationDefinition = <T extends SimulationDefinitions>(input: T): T => input;

export const BOILERS_CONTROL_DEFINITION = toControlDefinition({
  boilersPump: {
    yardTag: "50001022",
    componentType: ControlComponentType.Pump,
  },
  boilersHeatpump: {
    yardTag: "50001035",
    componentType: ControlComponentType.Heatpump,
  },
  boilersFlowcontrolLt2: {
    yardTag: "50001064-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  boilersFlowcontrolLt1: {
    yardTag: "50001064-08",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  boilersSwitchTank3Fill: {
    yardTag: "50001067-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank3BoostingReturn: {
    yardTag: "50001067-04",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank3Empty: {
    yardTag: "50001067-05",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank3BoostingSupply: {
    yardTag: "50001067-06",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2Fill: {
    yardTag: "50001067-07",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2BoostingReturn: {
    yardTag: "50001067-08",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2Empty: {
    yardTag: "50001067-09",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2BoostingSupply: {
    yardTag: "50001067-10",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1Fill: {
    yardTag: "50001067-11",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1BoostingReturn: {
    yardTag: "50001067-12",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1Empty: {
    yardTag: "50001067-13",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1BoostingSupply: {
    yardTag: "50001067-14",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchLowTemperature: {
    yardTag: "50001067-16",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchHeatpump: {
    yardTag: "50001067-17",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchHighTemperature: {
    yardTag: "50001067-18",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const BOILERS_PARAMETER_DEFINITION = toParameterDefinition({
  heatpumpFlowSetpoint: {
    componentType: ParametersType.Flow,
  },
  heatpumpTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
  htBoostingTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
  minimumTankTemperature: {
    componentType: ParametersType.Temperature,
  },
  maximumTankTemperature: {
    componentType: ParametersType.Temperature,
  },
  boostingDelta: {
    componentType: ParametersType.dT,
  },
  lt1FlowcontrolMinimumSetpoint: {
    componentType: ParametersType.Flow,
  },
  lt2FlowcontrolMinimumSetpoint: {
    componentType: ParametersType.Flow,
  },
  fillingTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
  minimumTankLevel: {
    componentType: ParametersType.Level,
  },
  maximumTankLevel: {
    componentType: ParametersType.Level,
  },
  tank1Disabled: {
    componentType: ParametersType.Disabled,
  },
  tank2Disabled: {
    componentType: ParametersType.Disabled,
  },
  tank3Disabled: {
    componentType: ParametersType.Disabled,
  },
  pumpTemperatureTuning: {
    componentType: ParametersType.Tuning,
  },
  pumpFlowTuning: {
    componentType: ParametersType.Tuning,
  },
  lt2FlowTuning: {
    componentType: ParametersType.Tuning,
  },
  lt1FlowTuning: {
    componentType: ParametersType.Tuning,
  },
});

export const BOILERS_SENSOR_DEFINITION = toSensorDefinition({
  boilersPump: {
    yardTag: "50001022",
    componentType: SensorComponentType.Pump,
  },
  boilersTemperatureHvacExchangerReturn: {
    yardTag: "50001038-25",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureLt2Return: {
    yardTag: "50001038-26",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureTank3: {
    yardTag: "50001038-27",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureTank2: {
    yardTag: "50001038-44",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureTank1: {
    yardTag: "50001038-45",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureLt1Return: {
    yardTag: "50001038-46",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureFreshwaterSupply: {
    yardTag: "50001038-47",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureFahrenheitReturn: {
    yardTag: "50001038-51",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureBoostingSupply: {
    yardTag: "50001038-65",
    componentType: SensorComponentType.Temperature,
  },
  boilersTemperatureBoostingReturn: {
    yardTag: "50001038-66",
    componentType: SensorComponentType.Temperature,
  },
  boilersLevelTank1: {
    yardTag: "50001056-01",
    componentType: SensorComponentType.Level,
  },
  boilersLevelTank2: {
    yardTag: "50001056-02",
    componentType: SensorComponentType.Level,
  },
  boilersLevelTank3: {
    yardTag: "50001056-03",
    componentType: SensorComponentType.Level,
  },
  boilersFlowLt2: {
    yardTag: "50001057-17",
    componentType: SensorComponentType.Flow,
  },
  boilersFlowLt1: {
    yardTag: "50001057-24",
    componentType: SensorComponentType.Flow,
  },
  boilersFlowBoosting: {
    yardTag: "50001058-11",
    componentType: SensorComponentType.Flow,
  },
  boilersFlowcontrolLt2: {
    yardTag: "50001064-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  boilersFlowcontrolLt1: {
    yardTag: "50001064-08",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  boilersSwitchTank3Fill: {
    yardTag: "50001067-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank3BoostingReturn: {
    yardTag: "50001067-04",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank3Empty: {
    yardTag: "50001067-05",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank3BoostingSupply: {
    yardTag: "50001067-06",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2Fill: {
    yardTag: "50001067-07",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2BoostingReturn: {
    yardTag: "50001067-08",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2Empty: {
    yardTag: "50001067-09",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank2BoostingSupply: {
    yardTag: "50001067-10",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1Fill: {
    yardTag: "50001067-11",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1BoostingReturn: {
    yardTag: "50001067-12",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1Empty: {
    yardTag: "50001067-13",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchTank1BoostingSupply: {
    yardTag: "50001067-14",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchLowTemperature: {
    yardTag: "50001067-16",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchHeatpump: {
    yardTag: "50001067-17",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersSwitchHighTemperature: {
    yardTag: "50001067-18",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  boilersPressureBoosting: {
    yardTag: "50001097-11",
    componentType: SensorComponentType.Pressure,
  },
  lt1FlowRecovery: {
    yardTag: "50001058-03",
    componentType: SensorComponentType.Flow,
  },
  lt1TemperatureRecovery: {
    yardTag: "50001038-16",
    componentType: SensorComponentType.Temperature,
  },
  consumersFlowBoosting: {
    yardTag: "50001058-07",
    componentType: SensorComponentType.Flow,
  },
  consumersTemperatureBoostingSupply: {
    yardTag: "50001038-53",
    componentType: SensorComponentType.Temperature,
  },
});

export const BOILERS_SIMULATION_INPUTS = toSimulationDefinition({
  boilersLt1Supply: {
    componentType: SimulationComponentType.Boundary,
  },
  boilersLt2Supply: {
    componentType: SimulationComponentType.Boundary,
  },
  boilersFahrenheitSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  boilersHtSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  boilersFreshwaterSupply: {
    componentType: SimulationComponentType.OverpressureTemperature,
  },
  boilersSeawaterSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  boilersHotwaterDemand: {
    componentType: SimulationComponentType.Flow,
  },
});

export const BOILERS_SIMULATION_OUTPUTS = toSimulationDefinition({
  boilersLt1Return: {
    componentType: SimulationComponentType.Temperature,
  },
  boilersLt2Return: {
    componentType: SimulationComponentType.Temperature,
  },
  boilersFahrenheitReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  boilersHtReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  boilersSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  boilersSeawaterSupply: {
    componentType: SimulationComponentType.Flow,
  },
  boilersFreshwaterReturn: {
    componentType: SimulationComponentType.Flow,
  },
});

export const CONSUMERS_CONTROL_DEFINITION = toControlDefinition({
  consumersFlowcontrolFahrenheit: {
    yardTag: "50001061",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolBypass: {
    yardTag: "50001062-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolBoosting: {
    yardTag: "50001065-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersSwitchFahrenheitExchanger: {
    yardTag: "50001066-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  consumersSwitchBoosting: {
    yardTag: "50001067-15",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const CONSUMERS_PARAMETER_DEFINITION = toParameterDefinition({
  boostingEnabled: {
    componentType: ParametersType.Enabled,
  },
  boostingFlowRatioSetpoint: {
    componentType: ParametersType.Flow,
  },
  fahrenheitEnabled: {
    componentType: ParametersType.Enabled,
  },
  fahrenheitFlowRatioSetpoint: {
    componentType: ParametersType.Flow,
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

export const CONSUMERS_SENSOR_DEFINITION = toSensorDefinition({
  consumersTemperatureBoostingReturn: {
    yardTag: "50001038-48",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureFahrenheitReturn: {
    yardTag: "50001038-49",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureBoostingSupply: {
    yardTag: "50001038-53",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureFahrenheitSupply: {
    yardTag: "50001038-54",
    componentType: SensorComponentType.Temperature,
  },
  consumersFlowBoosting: {
    yardTag: "50001058-07",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowFahrenheit: {
    yardTag: "50001058-08",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowBypass: {
    yardTag: "50001060-01",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowcontrolFahrenheit: {
    yardTag: "50001061",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolBypass: {
    yardTag: "50001062-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolBoosting: {
    yardTag: "50001065-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersSwitchFahrenheitExchanger: {
    yardTag: "50001066-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  consumersSwitchBoosting: {
    yardTag: "50001067-15",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const CONSUMERS_SIMULATION_INPUTS = toSimulationDefinition({
  consumersFahrenheitSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersBoostingSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersModuleSupply: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const CONSUMERS_SIMULATION_OUTPUTS = toSimulationDefinition({
  consumersFahrenheitReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersBoostingReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersModuleReturn: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const HIGH_TEMPERATURE_SIMULATION_INPUTS = toSimulationDefinition({
  thrustersAft: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersFwd: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersPcs: {
    componentType: SimulationComponentType.Pcs,
  },
  pvtMainFwd: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtMainAft: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtOwners: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmFreshwaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersFahrenheitSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersBoostingSupply: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const HIGH_TEMPERATURE_SIMULATION_OUTPUTS = toSimulationDefinition({
  thrustersSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  thrustersModuleSupply: {
    componentType: SimulationComponentType.Flow,
  },
  thrustersModuleReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtModuleReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtModuleSupply: {
    componentType: SimulationComponentType.Flow,
  },
  pvtSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersFahrenheitReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersBoostingReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersModuleReturn: {
    componentType: SimulationComponentType.Boundary,
  },
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

export const PCM_CONTROL_DEFINITION = toControlDefinition({
  pcmPump: {
    yardTag: "50001017",
    componentType: ControlComponentType.Pump,
  },
  pcmSwitchChargingReturn: {
    yardTag: "50001062-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmFlowcontrolModule1: {
    yardTag: "50001064-04",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmFlowcontrolModule2: {
    yardTag: "50001064-05",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmFlowcontrolModule3: {
    yardTag: "50001064-06",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmFlowcontrolModule4: {
    yardTag: "50001064-07",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmSwitchDischarging: {
    yardTag: "50001066-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchChargingSupply: {
    yardTag: "50001090-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchConsumers: {
    yardTag: "50001071-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmModule1: {
    yardTag: "50001049",
    componentType: ControlComponentType.Pcm,
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
    componentType: ParametersType.dT,
  },
  minimumChargingTemperature: {
    componentType: ParametersType.Temperature,
  },
  pumpTuning: {
    componentType: ParametersType.Tuning,
  },
  supplyingEnabled: {
    componentType: ParametersType.Enabled,
  },
  chargingEnabled: {
    componentType: ParametersType.Enabled,
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

export const PCM_SENSOR_DEFINITION = toSensorDefinition({
  pcmPump: {
    yardTag: "50001017",
    componentType: SensorComponentType.Pump,
  },
  pcmTemperatureProducersReturn: {
    yardTag: "50001038-31",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureProducersSupply: {
    yardTag: "50001038-55",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule1Out: {
    yardTag: "50001038-60",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule2Out: {
    yardTag: "50001038-33",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule3Out: {
    yardTag: "50001038-34",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule4Out: {
    yardTag: "50001038-35",
    componentType: SensorComponentType.Temperature,
  },
  pcmModule1: {
    yardTag: "50001049",
    componentType: SensorComponentType.Pcm,
  },
  pcmModule2: {
    yardTag: "50001050",
    componentType: SensorComponentType.Pcm,
  },
  pcmModule3: {
    yardTag: "50001051",
    componentType: SensorComponentType.Pcm,
  },
  pcmModule4: {
    yardTag: "50001052",
    componentType: SensorComponentType.Pcm,
  },
  pcmFlowModule1: {
    yardTag: "50001057-18",
    componentType: SensorComponentType.Flow,
  },
  pcmFlowModule2: {
    yardTag: "50001057-19",
    componentType: SensorComponentType.Flow,
  },
  pcmFlowModule3: {
    yardTag: "50001057-20",
    componentType: SensorComponentType.Flow,
  },
  pcmFlowModule4: {
    yardTag: "50001057-21",
    componentType: SensorComponentType.Flow,
  },
  pcmSwitchChargingReturn: {
    yardTag: "50001062-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmFlowcontrolModule1: {
    yardTag: "50001064-04",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmFlowcontrolModule2: {
    yardTag: "50001064-05",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmFlowcontrolModule3: {
    yardTag: "50001064-06",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmFlowcontrolModule4: {
    yardTag: "50001064-07",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  pcmSwitchDischarging: {
    yardTag: "50001066-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchChargingSupply: {
    yardTag: "50001090-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchConsumers: {
    yardTag: "50001071-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
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

export const PVT_CONTROL_DEFINITION = toControlDefinition({
  pvtPumpMainFwd: {
    yardTag: "50001018",
    componentType: ControlComponentType.Pump,
  },
  pvtPumpMainAft: {
    yardTag: "50001019",
    componentType: ControlComponentType.Pump,
  },
  pvtPumpOwners: {
    yardTag: "50001021",
    componentType: ControlComponentType.Pump,
  },
  pvtMixMainFwd: {
    yardTag: "50001044-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixMainAft: {
    yardTag: "50001044-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixOwners: {
    yardTag: "50001043-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtSwitchMainFwd: {
    yardTag: "50001067-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchMainAft: {
    yardTag: "50001067-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchOwners: {
    yardTag: "50001069-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtMixExchanger: {
    yardTag: "50001047-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
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
    componentType: ParametersType.Dutypoint,
  },
  mainAftMinimumPumpDutypoint: {
    componentType: ParametersType.Dutypoint,
  },
  ownersMinimumPumpDutypoint: {
    componentType: ParametersType.Dutypoint,
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

export const PVT_SENSOR_DEFINITION = toSensorDefinition({
  pvtPumpMainFwd: {
    yardTag: "50001018",
    componentType: SensorComponentType.Pump,
  },
  pvtPumpMainAft: {
    yardTag: "50001019",
    componentType: SensorComponentType.Pump,
  },
  pvtPumpOwners: {
    yardTag: "50001021",
    componentType: SensorComponentType.Pump,
  },
  pvtTemperatureMainFwdReturn: {
    yardTag: "50001038-03",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainFwdSupply: {
    yardTag: "50001038-23",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainAftReturn: {
    yardTag: "50001038-73",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainAftSupply: {
    yardTag: "50001038-22",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersSupply: {
    yardTag: "50001038-21",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersReturn: {
    yardTag: "50001038-04",
    componentType: SensorComponentType.Temperature,
  },
  pvtMixMainFwd: {
    yardTag: "50001044-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixMainAft: {
    yardTag: "50001044-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixOwners: {
    yardTag: "50001043-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtFlowMainFwdRecovery: {
    yardTag: "50001058-12",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainAftRecovery: {
    yardTag: "50001058-13",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersRecovery: {
    yardTag: "50001057-03",
    componentType: SensorComponentType.Flow,
  },
  pvtPressureMainFwd: {
    yardTag: "50001097-03",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureMainAft: {
    yardTag: "50001097-04",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureOwners: {
    yardTag: "50001097-05",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureSupply: {
    yardTag: "50001097-06",
    componentType: SensorComponentType.Pressure,
  },
  pvtSwitchMainFwd: {
    yardTag: "50001067-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchMainAft: {
    yardTag: "50001067-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchOwners: {
    yardTag: "50001069-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtMixExchanger: {
    yardTag: "50001047-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtTemperatureSupply: {
    yardTag: "50001038-24",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString11Return: {
    yardTag: "50009005-01",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString12Return: {
    yardTag: "50009005-19",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString21Return: {
    yardTag: "50009005-03",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString22Return: {
    yardTag: "50009005-04",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString3Return: {
    yardTag: "50009005-05",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString4Return: {
    yardTag: "50009005-06",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString51Return: {
    yardTag: "50009005-07",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString52Return: {
    yardTag: "50009005-08",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString61Return: {
    yardTag: "50009005-09",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString62Return: {
    yardTag: "50009005-10",
    componentType: SensorComponentType.Temperature,
  },
  pvtFlowMainString11: {
    yardTag: "50009006-01",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString12: {
    yardTag: "50009009-05",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString21: {
    yardTag: "50009006-03",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString22: {
    yardTag: "50009006-04",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString3: {
    yardTag: "50009009-01",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString4: {
    yardTag: "50009009-02",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString51: {
    yardTag: "50009006-05",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString52: {
    yardTag: "50009006-06",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString61: {
    yardTag: "50009006-07",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString62: {
    yardTag: "50009006-08",
    componentType: SensorComponentType.Flow,
  },
  pvtTemperatureMainString1Supply: {
    yardTag: "50009005-26",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString2Supply: {
    yardTag: "50009005-25",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString3Supply: {
    yardTag: "50009005-24",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString4Supply: {
    yardTag: "50009005-23",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString5Supply: {
    yardTag: "50009005-22",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString6Supply: {
    yardTag: "50009005-21",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString71Return: {
    yardTag: "50009005-11",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString72Return: {
    yardTag: "50009005-12",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString81Return: {
    yardTag: "50009005-13",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString82Return: {
    yardTag: "50009005-14",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString9Return: {
    yardTag: "50009005-15",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString10Return: {
    yardTag: "50009005-16",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString111Return: {
    yardTag: "50009005-17",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString112Return: {
    yardTag: "50009005-18",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString13Return: {
    yardTag: "50009005-20",
    componentType: SensorComponentType.Temperature,
  },
  pvtFlowMainString71: {
    yardTag: "50009006-09",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString72: {
    yardTag: "50009006-10",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString81: {
    yardTag: "50009006-11",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString82: {
    yardTag: "50009006-12",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString9: {
    yardTag: "50009009-03",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString10: {
    yardTag: "50009009-04",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString111: {
    yardTag: "50009006-13",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString112: {
    yardTag: "50009006-14",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString13: {
    yardTag: "50009009-06",
    componentType: SensorComponentType.Flow,
  },
  pvtTemperatureMainString7Supply: {
    yardTag: "50009005-27",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString8Supply: {
    yardTag: "50009005-28",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString9Supply: {
    yardTag: "50009005-29",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString10Supply: {
    yardTag: "50009005-30",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString11Supply: {
    yardTag: "50009005-31",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString12Supply: {
    yardTag: "50009005-32",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString13Supply: {
    yardTag: "50009005-33",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString1Return: {
    yardTag: "50009005-34",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString2Return: {
    yardTag: "50009005-35",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString3Return: {
    yardTag: "50009005-36",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString4Return: {
    yardTag: "50009005-37",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString5Return: {
    yardTag: "50009005-38",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString6Return: {
    yardTag: "50009005-39",
    componentType: SensorComponentType.Temperature,
  },
  pvtFlowOwnersString1: {
    yardTag: "50009009-07",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString2: {
    yardTag: "50009009-08",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString3: {
    yardTag: "50009009-09",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString4: {
    yardTag: "50009009-10",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString5: {
    yardTag: "50009009-11",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowOwnersString6: {
    yardTag: "50009009-12",
    componentType: SensorComponentType.Flow,
  },
  pvtTemperatureOwnersString1Supply: {
    yardTag: "50009005-40",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString2Supply: {
    yardTag: "50009005-41",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString3Supply: {
    yardTag: "50009005-42",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString4Supply: {
    yardTag: "50009005-43",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString5Supply: {
    yardTag: "50009005-44",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString6Supply: {
    yardTag: "50009005-45",
    componentType: SensorComponentType.Temperature,
  },
});

export const PVT_SIMULATION_INPUTS = toSimulationDefinition({
  pvtMainFwd: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtMainAft: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtOwners: {
    componentType: SimulationComponentType.HeatSource,
  },
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

export const THRUSTERS_CONTROL_DEFINITION = toControlDefinition({
  thrustersPump1: {
    yardTag: "50001194",
    componentType: ControlComponentType.Pump,
  },
  thrustersPump2: {
    yardTag: "50001195",
    componentType: ControlComponentType.Pump,
  },
  thrustersMixRecovery: {
    yardTag: "50001074",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersMixExchanger: {
    yardTag: "50001214-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersFlowcontrolAft: {
    yardTag: "50001215",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  thrustersFlowcontrolFwd: {
    yardTag: "50001064-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  thrustersShutoffRecovery: {
    yardTag: "50001066-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Shutoff,
  },
  thrustersSwitchAft: {
    yardTag: "50001091-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  thrustersSwitchFwd: {
    yardTag: "50001091-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
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

export const THRUSTERS_SENSOR_DEFINITION = toSensorDefinition({
  thrustersPump1: {
    yardTag: "50001194",
    componentType: SensorComponentType.Pump,
  },
  thrustersPump2: {
    yardTag: "50001195",
    componentType: SensorComponentType.Pump,
  },
  thrustersTemperatureAftReturn: {
    yardTag: "50001038-01",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureFwdReturn: {
    yardTag: "50001038-02",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureSupply: {
    yardTag: "50001038-28",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureRecoveryMix: {
    yardTag: "50001038-30",
    componentType: SensorComponentType.Temperature,
  },
  thrustersMixRecovery: {
    yardTag: "50001074",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersMixExchanger: {
    yardTag: "50001214-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersFlowFwd: {
    yardTag: "50001057-22",
    componentType: SensorComponentType.Flow,
  },
  thrustersFlowAft: {
    yardTag: "50001218-02",
    componentType: SensorComponentType.Flow,
  },
  thrustersFlowcontrolAft: {
    yardTag: "50001215",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  thrustersFlowcontrolFwd: {
    yardTag: "50001064-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  thrustersShutoffRecovery: {
    yardTag: "50001066-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Shutoff,
  },
  thrustersSwitchAft: {
    yardTag: "50001091-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  thrustersSwitchFwd: {
    yardTag: "50001091-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  thrustersFlowRecovery: {
    yardTag: "50001218-01",
    componentType: SensorComponentType.Flow,
  },
  thrustersPressurePump: {
    yardTag: "50001097-01",
    componentType: SensorComponentType.Pressure,
  },
  thrustersPressureRelief: {
    yardTag: "50001097-02",
    componentType: SensorComponentType.Pressure,
  },
  thrustersAft: {
    yardTag: "15001001",
    componentType: SensorComponentType.Thruster,
  },
  thrustersFwd: {
    yardTag: "15001002",
    componentType: SensorComponentType.Thruster,
  },
  thrustersPcs: {
    yardTag: "1500",
    componentType: SensorComponentType.Pcs,
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
