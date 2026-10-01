import {
  ControlComponentType,
  ControlDefinitions,
  ControllerStateComponentType,
  ControllerStateDefinitions,
  ParameterDefinitions,
  ParametersType,
  SensorComponentType,
  SensorDefinitions,
  SimulationComponentType,
  SimulationDefinitions,
  ValveType,
} from "@/modules/thrsim/types";

const toControlDefinition = <T extends ControlDefinitions>(input: T): T => input;
const toSensorDefinition = <T extends SensorDefinitions>(input: T): T => input;
const toParameterDefinition = <T extends ParameterDefinitions>(input: T): T => input;
const toSimulationDefinition = <T extends SimulationDefinitions>(input: T): T => input;
const toControllerStateDefinition = <T extends ControllerStateDefinitions>(input: T): T => input;

export const ADSORPTION_CONTROL_DEFINITION = toControlDefinition({
  adsorptionChiller: {
    yardTag: "50001034",
    componentType: ControlComponentType.AdsorptionChiller,
  },
  adsorptionFlowcontrolWaste: {
    yardTag: "50001062-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  adsorptionMixHot: {
    yardTag: "50001046-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  adsorptionMixWaste: {
    yardTag: "50001047-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  adsorptionSwitchDhw: {
    yardTag: "50001187-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const ADSORPTION_CONTROLLER_STATE = toControllerStateDefinition({});

export const ADSORPTION_PARAMETER_DEFINITION = toParameterDefinition({
  adsorptionColdMinimum: {
    componentType: ParametersType.Temperature,
  },
  adsorptionColdTrigger: {
    componentType: ParametersType.Temperature,
  },
  adsorptionCoolingSetpoint: {
    componentType: ParametersType.Temperature,
  },
  adsorptionHotMinimum: {
    componentType: ParametersType.Temperature,
  },
  adsorptionHotTrigger: {
    componentType: ParametersType.Temperature,
  },
  chillerEnabled: {
    componentType: ParametersType.Enabled,
  },
  freeCoolingEnabled: {
    componentType: ParametersType.Enabled,
  },
  hotMixTuning: {
    componentType: ParametersType.Tuning,
  },
  hotSupplyTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
  recoveryTuning: {
    componentType: ParametersType.Tuning,
  },
  wasteCoolingTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
  wasteCoolingTuning: {
    componentType: ParametersType.Tuning,
  },
  wasteRecoveryTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
});

export const ADSORPTION_SENSOR_DEFINITION = toSensorDefinition({
  adsorptionAvailableColdTemperature: {
    componentType: SensorComponentType.Temperature,
  },
  adsorptionAvailableHotTemperature: {
    componentType: SensorComponentType.Temperature,
  },
  adsorptionAvailableSeawaterTemperature: {
    componentType: SensorComponentType.Temperature,
  },
  adsorptionChiller: {
    yardTag: "50001034",
    componentType: SensorComponentType.AdsorptionChiller,
  },
  adsorptionDhwExchanger: {
    yardTag: "50001004",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  adsorptionFlowDhw: {
    yardTag: "50001058-10",
    componentType: SensorComponentType.Flow,
  },
  adsorptionFlowHot: {
    yardTag: "50001058-02",
    componentType: SensorComponentType.Flow,
  },
  adsorptionFlowHt: {
    yardTag: "50001058-09",
    componentType: SensorComponentType.Flow,
  },
  adsorptionFlowWaste: {
    yardTag: "50001059",
    componentType: SensorComponentType.Flow,
  },
  adsorptionFlowcontrolWaste: {
    yardTag: "50001062-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  adsorptionHtExchanger: {
    yardTag: "50001003",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  adsorptionMixHot: {
    yardTag: "50001046-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  adsorptionMixWaste: {
    yardTag: "50001047-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  adsorptionSwitchDhw: {
    yardTag: "50001187-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  adsorptionTemperatureDhwReturn: {
    yardTag: "50001038-56",
    componentType: SensorComponentType.Temperature,
  },
  adsorptionTemperatureHotReturn: {
    yardTag: "50001038-36",
    componentType: SensorComponentType.Temperature,
  },
  adsorptionTemperatureHotSupply: {
    yardTag: "50001038-37",
    componentType: SensorComponentType.Temperature,
  },
  adsorptionTemperatureHtReturn: {
    yardTag: "50001038-41",
    componentType: SensorComponentType.Temperature,
  },
  adsorptionTemperatureHtSupply: {
    yardTag: "50001038-50",
    componentType: SensorComponentType.Temperature,
  },
  adsorptionTemperatureWasteReturn: {
    yardTag: "50001038-38",
    componentType: SensorComponentType.Temperature,
  },
  adsorptionTemperatureWasteSupply: {
    yardTag: "50001038-39",
    componentType: SensorComponentType.Temperature,
  },
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
  },
});

export const ADSORPTION_SIMULATION_INPUTS = toSimulationDefinition({
  adsorptionAvailableColdTemperature: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionAvailableHotTemperature: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionAvailableSeawaterTemperature: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionChiller: {
    componentType: SimulationComponentType.AdsorptionChiller,
  },
  adsorptionConsumersSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  adsorptionCoolingSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionDhwSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  adsorptionSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
});

export const ADSORPTION_SIMULATION_OUTPUTS = toSimulationDefinition({
  adsorptionConsumersReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionCoolingReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  adsorptionDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});

export const CONSUMERS_CONTROL_DEFINITION = toControlDefinition({
  consumersFlowcontrolAdsorption: {
    yardTag: "50001061",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolBypass: {
    yardTag: "50001062-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolDhw: {
    yardTag: "50001065-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersSwitchAdsorption: {
    yardTag: "50001066-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  consumersSwitchDhw: {
    yardTag: "50001067-15",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const CONSUMERS_CONTROLLER_STATE = toControllerStateDefinition({});

export const CONSUMERS_PARAMETER_DEFINITION = toParameterDefinition({
  adsorptionEnabled: {
    componentType: ParametersType.Enabled,
  },
  adsorptionFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  adsorptionFlowRatioSetpoint: {
    componentType: ParametersType.Flow,
  },
  bypassFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  dhwEnabled: {
    componentType: ParametersType.Enabled,
  },
  dhwFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  dhwFlowRatioSetpoint: {
    componentType: ParametersType.Flow,
  },
});

export const CONSUMERS_SENSOR_DEFINITION = toSensorDefinition({
  consumersAdsorptionExchanger: {
    yardTag: "50001003",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  consumersDhwExchanger: {
    yardTag: "50001007",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  consumersFlowAdsorption: {
    yardTag: "50001058-08",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowBypass: {
    yardTag: "50001192",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowDhw: {
    yardTag: "50001058-07",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowcontrolAdsorption: {
    yardTag: "50001061",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolBypass: {
    yardTag: "50001062-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersFlowcontrolDhw: {
    yardTag: "50001065-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  consumersSwitchAdsorption: {
    yardTag: "50001066-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  consumersSwitchDhw: {
    yardTag: "50001067-15",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  consumersTemperatureAdsorptionReturn: {
    yardTag: "50001038-49",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureAdsorptionSupply: {
    yardTag: "50001038-54",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureDhwReturn: {
    yardTag: "50001038-48",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureDhwSupply: {
    yardTag: "50001038-53",
    componentType: SensorComponentType.Temperature,
  },
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
  },
});

export const CONSUMERS_SIMULATION_INPUTS = toSimulationDefinition({
  consumersAdsorptionSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersDhwSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersPcmSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
});

export const CONSUMERS_SIMULATION_OUTPUTS = toSimulationDefinition({
  consumersAdsorptionReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const DC_CONTROL_DEFINITION = toControlDefinition({
  dcMixAft: {
    yardTag: "50001043-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixExchanger: {
    yardTag: "50001046-05",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixFwd: {
    yardTag: "50001042-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixRecovery: {
    yardTag: "50001046-04",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixUgrid: {
    yardTag: "50001045-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcPumpAft: {
    yardTag: "50001020",
    componentType: ControlComponentType.Pump,
  },
  dcPumpFwd: {
    yardTag: "50001025",
    componentType: ControlComponentType.Pump,
  },
  dcPumpUgrid: {
    yardTag: "50001023",
    componentType: ControlComponentType.Pump,
  },
  dcSwitchAft1: {
    yardTag: "50001068-04",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchAft2: {
    yardTag: "50001068-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchAft3: {
    yardTag: "50001068-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchAft4: {
    yardTag: "50001068-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchFwd1: {
    yardTag: "50001068-06",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchFwd2: {
    yardTag: "50001068-05",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchUgrid1: {
    yardTag: "50001069-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchUgrid2: {
    yardTag: "50001069-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const DC_CONTROLLER_STATE = toControllerStateDefinition({});

export const DC_PARAMETER_DEFINITION = toParameterDefinition({
  brightloopFlowSetpoint: {
    componentType: ParametersType.Flow,
  },
  brightloopReturnTemperature: {
    componentType: ParametersType.Temperature,
  },
  brightloopsAftMixTuning: {
    componentType: ParametersType.Tuning,
  },
  brightloopsAftPumpTuning: {
    componentType: ParametersType.Tuning,
  },
  brightloopsFwdMixTuning: {
    componentType: ParametersType.Tuning,
  },
  brightloopsFwdPumpTuning: {
    componentType: ParametersType.Tuning,
  },
  heatDumpTuning: {
    componentType: ParametersType.Tuning,
  },
  maximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
  recoveryMixTuning: {
    componentType: ParametersType.Tuning,
  },
  recoveryTemperature: {
    componentType: ParametersType.Temperature,
  },
  ugridFlowSetpoint: {
    componentType: ParametersType.Flow,
  },
  ugridReturnTemperature: {
    componentType: ParametersType.Temperature,
  },
  ugridsMixTuning: {
    componentType: ParametersType.Tuning,
  },
  ugridsPumpTuning: {
    componentType: ParametersType.Tuning,
  },
});

export const DC_SENSOR_DEFINITION = toSensorDefinition({
  dcAftFlow: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  dcAftHeat: {
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dcBrightloopAft1: {
    yardTag: "45002076",
    componentType: SensorComponentType.Brightloop,
  },
  dcBrightloopAft2: {
    yardTag: "45002075",
    componentType: SensorComponentType.Brightloop,
  },
  dcBrightloopAft3: {
    yardTag: "45002074",
    componentType: SensorComponentType.Brightloop,
  },
  dcBrightloopAft4: {
    yardTag: "45002073",
    componentType: SensorComponentType.Brightloop,
  },
  dcBrightloopFwd1: {
    yardTag: "45002078",
    componentType: SensorComponentType.Brightloop,
  },
  dcBrightloopFwd2: {
    yardTag: "45002077",
    componentType: SensorComponentType.Brightloop,
  },
  dcDhwExchanger: {
    yardTag: "50001008",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dcFlowAft1: {
    yardTag: "50001057-07",
    componentType: SensorComponentType.Flow,
  },
  dcFlowAft2: {
    yardTag: "50001057-06",
    componentType: SensorComponentType.Flow,
  },
  dcFlowAft3: {
    yardTag: "50001057-05",
    componentType: SensorComponentType.Flow,
  },
  dcFlowAft4: {
    yardTag: "50001057-04",
    componentType: SensorComponentType.Flow,
  },
  dcFlowAftReturn: {
    yardTag: "50001057-25",
    componentType: SensorComponentType.Flow,
  },
  dcFlowFwd1: {
    yardTag: "50001057-12",
    componentType: SensorComponentType.Flow,
  },
  dcFlowFwd2: {
    yardTag: "50001057-11",
    componentType: SensorComponentType.Flow,
  },
  dcFlowFwdReturn: {
    yardTag: "50001057-26",
    componentType: SensorComponentType.Flow,
  },
  dcFlowRecovery: {
    yardTag: "50001058-04",
    componentType: SensorComponentType.Flow,
  },
  dcFlowUgrid1: {
    yardTag: "50001057-09",
    componentType: SensorComponentType.Flow,
  },
  dcFlowUgrid2: {
    yardTag: "50001057-08",
    componentType: SensorComponentType.Flow,
  },
  dcFlowUgridReturn: {
    yardTag: "50001058-06",
    componentType: SensorComponentType.Flow,
  },
  dcFwdFlow: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  dcFwdHeat: {
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dcMixAft: {
    yardTag: "50001043-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixExchanger: {
    yardTag: "50001046-05",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixFwd: {
    yardTag: "50001042-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixRecovery: {
    yardTag: "50001046-04",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcMixUgrid: {
    yardTag: "50001045-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  dcPressureAft: {
    yardTag: "50001097-07",
    componentType: SensorComponentType.Pressure,
  },
  dcPressureFwd: {
    yardTag: "50001097-09",
    componentType: SensorComponentType.Pressure,
  },
  dcPressureUgrid: {
    yardTag: "50001097-08",
    componentType: SensorComponentType.Pressure,
  },
  dcPumpAft: {
    yardTag: "50001020",
    componentType: SensorComponentType.Pump,
  },
  dcPumpFwd: {
    yardTag: "50001025",
    componentType: SensorComponentType.Pump,
  },
  dcPumpUgrid: {
    yardTag: "50001023",
    componentType: SensorComponentType.Pump,
  },
  dcSeawaterExchanger: {
    yardTag: "50001006",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dcSwitchAft1: {
    yardTag: "50001068-04",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchAft2: {
    yardTag: "50001068-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchAft3: {
    yardTag: "50001068-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchAft4: {
    yardTag: "50001068-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchFwd1: {
    yardTag: "50001068-06",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchFwd2: {
    yardTag: "50001068-05",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchUgrid1: {
    yardTag: "50001069-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcSwitchUgrid2: {
    yardTag: "50001069-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dcTemperatureAft1Return: {
    yardTag: "50001038-08",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureAft2Return: {
    yardTag: "50001038-07",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureAft3Return: {
    yardTag: "50001038-06",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureAft4Return: {
    yardTag: "50001038-05",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureAftReturn: {
    yardTag: "50001038-20",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureAftSupply: {
    yardTag: "50001038-15",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureFwd1Return: {
    yardTag: "50001038-13",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureFwd2Return: {
    yardTag: "50001038-12",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureFwdReturn: {
    yardTag: "50001038-19",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureFwdSupply: {
    yardTag: "50001038-69",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureRecovery: {
    yardTag: "50001038-52",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureRecoveryMix: {
    yardTag: "50001038-17",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureRecoveryReturn: {
    yardTag: "50001038-58",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureSupply: {
    yardTag: "50001038-18",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureUgrid1Return: {
    yardTag: "50001038-10",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureUgrid2Return: {
    yardTag: "50001038-09",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureUgridReturn: {
    yardTag: "50001038-71",
    componentType: SensorComponentType.Temperature,
  },
  dcTemperatureUgridSupply: {
    yardTag: "50001038-70",
    componentType: SensorComponentType.Temperature,
  },
  dcTotalFlow: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  dcUgrid1: {
    yardTag: "45002082",
    componentType: SensorComponentType.Ugrid,
  },
  dcUgrid2: {
    yardTag: "45002081",
    componentType: SensorComponentType.Ugrid,
  },
  dcUgridFlow: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  dcUgridHeat: {
    componentType: SensorComponentType.HeatTransferDevice,
  },
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
  },
});

export const DC_SIMULATION_INPUTS = toSimulationDefinition({
  dcBrightloopAft1: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopAft2: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopAft3: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopAft4: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopFwd1: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopFwd2: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcDhwSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dcSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dcUgrid1: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcUgrid2: {
    componentType: SimulationComponentType.HeatSource,
  },
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
});

export const DC_SIMULATION_OUTPUTS = toSimulationDefinition({
  dcDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dcSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});

export const DHW_CONTROL_DEFINITION = toControlDefinition({
  dhwFlowcontrolDc: {
    yardTag: "50001064-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  dhwFlowcontrolDrives: {
    yardTag: "50001064-08",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  dhwHeatpump: {
    yardTag: "50001035",
    componentType: ControlComponentType.Heatpump,
  },
  dhwPump: {
    yardTag: "50001022",
    componentType: ControlComponentType.Pump,
  },
  dhwSwitchHeatpump: {
    yardTag: "50001067-17",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchHighTemperature: {
    yardTag: "50001067-18",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchLowTemperature: {
    yardTag: "50001067-16",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1BoostingReturn: {
    yardTag: "50001067-12",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1BoostingSupply: {
    yardTag: "50001067-14",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1Inlet: {
    yardTag: "50001067-11",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1Outlet: {
    yardTag: "50001067-13",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2BoostingReturn: {
    yardTag: "50001067-08",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2BoostingSupply: {
    yardTag: "50001067-10",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2Inlet: {
    yardTag: "50001067-07",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2Outlet: {
    yardTag: "50001067-09",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3BoostingReturn: {
    yardTag: "50001067-04",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3BoostingSupply: {
    yardTag: "50001067-06",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3Inlet: {
    yardTag: "50001067-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3Outlet: {
    yardTag: "50001067-05",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const DHW_CONTROLLER_STATE = toControllerStateDefinition({
  dhwDcFlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  dhwDrivesFlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  dhwPumpFlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  dhwTanksController: {
    componentType: ControllerStateComponentType.DhwTanksController,
  },
});

export const DHW_PARAMETER_DEFINITION = toParameterDefinition({
  boostingMinimumHeat: {
    componentType: ParametersType.Power,
  },
  boostingStallCooldown: {
    componentType: ParametersType.Duration,
  },
  boostingStallWindow: {
    componentType: ParametersType.Duration,
  },
  boostingStartupGrace: {
    componentType: ParametersType.Duration,
  },
  dcFlowTuning: {
    componentType: ParametersType.Tuning,
  },
  dcFlowcontrolMinimumSetpoint: {
    componentType: ParametersType.FlowControl,
  },
  drivesFlowTuning: {
    componentType: ParametersType.Tuning,
  },
  drivesFlowcontrolMinimumSetpoint: {
    componentType: ParametersType.FlowControl,
  },
  fillingTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
  fullLevelLowerBand: {
    componentType: ParametersType.Level,
  },
  heatpumpBoostingEnabled: {
    componentType: ParametersType.Enabled,
  },
  heatpumpFlowSetpoint: {
    componentType: ParametersType.Flow,
  },
  heatpumpTemperatureSetpoint: {
    componentType: ParametersType.Temperature,
  },
  htBoostingEnabled: {
    componentType: ParametersType.Enabled,
  },
  htBoostingFlowSetpoint: {
    componentType: ParametersType.Flow,
  },
  htBoostingMinimumDelta: {
    componentType: ParametersType.dT,
  },
  maximumTankLevel: {
    componentType: ParametersType.Level,
  },
  maximumTankTemperature: {
    componentType: ParametersType.Temperature,
  },
  minimumPumpDutypoint: {
    componentType: ParametersType.Dutypoint,
  },
  minimumTankLevel: {
    componentType: ParametersType.Level,
  },
  minimumTankTemperature: {
    componentType: ParametersType.Temperature,
  },
  pumpFlowTuning: {
    componentType: ParametersType.Tuning,
  },
  tank1Enabled: {
    componentType: ParametersType.Enabled,
  },
  tank2Enabled: {
    componentType: ParametersType.Enabled,
  },
  tank3Enabled: {
    componentType: ParametersType.Enabled,
  },
});

export const DHW_SENSOR_DEFINITION = toSensorDefinition({
  consumersFlowDhw: {
    yardTag: "50001058-07",
    componentType: SensorComponentType.Flow,
  },
  consumersTemperatureDhwSupply: {
    yardTag: "50001038-53",
    componentType: SensorComponentType.Temperature,
  },
  dcFlowRecovery: {
    yardTag: "50001058-04",
    componentType: SensorComponentType.Flow,
  },
  dcTemperatureRecovery: {
    yardTag: "50001038-52",
    componentType: SensorComponentType.Temperature,
  },
  dhwAdsorptionExchanger: {
    yardTag: "50001004",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dhwConsumersExchanger: {
    yardTag: "50001007",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dhwDcExchanger: {
    yardTag: "50001008",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dhwDrivesExchanger: {
    yardTag: "50001009",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dhwFlowBoosting: {
    yardTag: "50001058-11",
    componentType: SensorComponentType.Flow,
  },
  dhwFlowDc: {
    yardTag: "50001057-17",
    componentType: SensorComponentType.Flow,
  },
  dhwFlowDrives: {
    yardTag: "50001057-24",
    componentType: SensorComponentType.Flow,
  },
  dhwFlowcontrolDc: {
    yardTag: "50001064-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  dhwFlowcontrolDrives: {
    yardTag: "50001064-08",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  dhwFreshwaterFlowSupply: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  dhwHeatpump: {
    yardTag: "50001035",
    componentType: SensorComponentType.HeatPump,
  },
  dhwHeatpumpHeat: {
    yardTag: "50001035",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dhwHvacExchanger: {
    yardTag: "41001001",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  dhwLevelSwitchTank1: {
    yardTag: "50001098-01",
    componentType: SensorComponentType.LevelSwitch,
  },
  dhwLevelSwitchTank2: {
    yardTag: "50001098-02",
    componentType: SensorComponentType.LevelSwitch,
  },
  dhwLevelSwitchTank3: {
    yardTag: "50001098-03",
    componentType: SensorComponentType.LevelSwitch,
  },
  dhwLevelTank1: {
    yardTag: "50001056-01",
    componentType: SensorComponentType.Level,
  },
  dhwLevelTank2: {
    yardTag: "50001056-02",
    componentType: SensorComponentType.Level,
  },
  dhwLevelTank3: {
    yardTag: "50001056-03",
    componentType: SensorComponentType.Level,
  },
  dhwPressure: {
    yardTag: "50001097-11",
    componentType: SensorComponentType.Pressure,
  },
  dhwPump: {
    yardTag: "50001022",
    componentType: SensorComponentType.Pump,
  },
  dhwSwitchHeatpump: {
    yardTag: "50001067-17",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchHighTemperature: {
    yardTag: "50001067-18",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchLowTemperature: {
    yardTag: "50001067-16",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1BoostingReturn: {
    yardTag: "50001067-12",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1BoostingSupply: {
    yardTag: "50001067-14",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1Inlet: {
    yardTag: "50001067-11",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank1Outlet: {
    yardTag: "50001067-13",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2BoostingReturn: {
    yardTag: "50001067-08",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2BoostingSupply: {
    yardTag: "50001067-10",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2Inlet: {
    yardTag: "50001067-07",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank2Outlet: {
    yardTag: "50001067-09",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3BoostingReturn: {
    yardTag: "50001067-04",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3BoostingSupply: {
    yardTag: "50001067-06",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3Inlet: {
    yardTag: "50001067-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwSwitchTank3Outlet: {
    yardTag: "50001067-05",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  dhwTemperatureAdsorptionReturn: {
    yardTag: "50001038-51",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureBoostingReturn: {
    yardTag: "50001038-65",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureBoostingSupply: {
    yardTag: "50001038-66",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureDcReturn: {
    yardTag: "50001038-26",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureDrivesReturn: {
    yardTag: "50001038-46",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureFreshwaterSupply: {
    yardTag: "50001038-47",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureHvacExchangerReturn: {
    yardTag: "50001038-25",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureTank1: {
    yardTag: "50001038-45",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureTank2: {
    yardTag: "50001038-44",
    componentType: SensorComponentType.Temperature,
  },
  dhwTemperatureTank3: {
    yardTag: "50001038-27",
    componentType: SensorComponentType.Temperature,
  },
  drivesFlowRecovery: {
    yardTag: "50001058-03",
    componentType: SensorComponentType.Flow,
  },
  drivesTemperatureRecovery: {
    yardTag: "50001038-16",
    componentType: SensorComponentType.Temperature,
  },
  freshwaterHotwaterFlow: {
    yardTag: "25001123-1",
    componentType: SensorComponentType.FlowOnly,
  },
  freshwaterHotwaterTemperature: {
    yardTag: "25001038-1",
    componentType: SensorComponentType.Temperature,
  },
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
  },
});

export const DHW_SIMULATION_INPUTS = toSimulationDefinition({
  dhwAdsorptionSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dhwConsumersSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dhwDcSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dhwDrivesSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dhwFreshwaterSupply: {
    componentType: SimulationComponentType.OverpressureTemperature,
  },
  dhwHotwaterDemand: {
    componentType: SimulationComponentType.Flow,
  },
  dhwHvacExchanger: {
    componentType: SimulationComponentType.HvacExchanger,
  },
  dhwSeawaterSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
});

export const DHW_SIMULATION_OUTPUTS = toSimulationDefinition({
  dhwAdsorptionReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwConsumersReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwDcReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwDrivesReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwFreshwaterReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  dhwSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwSeawaterSupply: {
    componentType: SimulationComponentType.Flow,
  },
});

export const DRIVES_CONTROL_DEFINITION = toControlDefinition({
  drivesFlowcontrolPropdriveAft: {
    yardTag: "50001065-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  drivesFlowcontrolPropdriveFwd: {
    yardTag: "50001065-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  drivesMixExchanger: {
    yardTag: "50001046-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  drivesMixRecovery: {
    yardTag: "50001046-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  drivesPump1: {
    yardTag: "50001028",
    componentType: ControlComponentType.Pump,
  },
  drivesPump2: {
    yardTag: "50001029",
    componentType: ControlComponentType.Pump,
  },
  drivesSwitchPropdriveAft1: {
    yardTag: "50001069-06",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchPropdriveAft2: {
    yardTag: "50001069-09",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchPropdriveFwd1: {
    yardTag: "50001069-07",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchPropdriveFwd2: {
    yardTag: "50001069-08",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchShorepowerReturn: {
    yardTag: "50001069-05",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchShorepowerSupply: {
    yardTag: "50001069-04",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const DRIVES_CONTROLLER_STATE = toControllerStateDefinition({});

export const DRIVES_PARAMETER_DEFINITION = toParameterDefinition({
  aftFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  fwdFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  heatDumpTuning: {
    componentType: ParametersType.Tuning,
  },
  propulsionDrivesFlowSetpoint: {
    componentType: ParametersType.Flow,
  },
  propulsionMaximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
  pumpTuning: {
    componentType: ParametersType.Tuning,
  },
  recoveryMixTuning: {
    componentType: ParametersType.Tuning,
  },
  recoveryTemperature: {
    componentType: ParametersType.Temperature,
  },
  shorepowerFlowSetpoint: {
    componentType: ParametersType.Flow,
  },
  shorepowerMaximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
});

export const DRIVES_SENSOR_DEFINITION = toSensorDefinition({
  drivesDhwExchanger: {
    yardTag: "50001009",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  drivesFlowPropdriveAft1: {
    yardTag: "50001057-13",
    componentType: SensorComponentType.Flow,
  },
  drivesFlowPropdriveAft2: {
    yardTag: "50001057-16",
    componentType: SensorComponentType.Flow,
  },
  drivesFlowPropdriveFwd1: {
    yardTag: "50001057-15",
    componentType: SensorComponentType.Flow,
  },
  drivesFlowPropdriveFwd2: {
    yardTag: "50001057-14",
    componentType: SensorComponentType.Flow,
  },
  drivesFlowRecovery: {
    yardTag: "50001058-03",
    componentType: SensorComponentType.Flow,
  },
  drivesFlowShorepower: {
    yardTag: "50001057-10",
    componentType: SensorComponentType.Flow,
  },
  drivesFlowcontrolPropdriveAft: {
    yardTag: "50001065-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  drivesFlowcontrolPropdriveFwd: {
    yardTag: "50001065-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.FlowControl,
  },
  drivesMixExchanger: {
    yardTag: "50001046-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  drivesMixRecovery: {
    yardTag: "50001046-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  drivesPressure: {
    yardTag: "50001097-10",
    componentType: SensorComponentType.Pressure,
  },
  drivesPropdriveAft1: {
    yardTag: "45002079",
    componentType: SensorComponentType.PropulsionDrive,
  },
  drivesPropdriveAft2: {
    yardTag: "45002079",
    componentType: SensorComponentType.PropulsionDrive,
  },
  drivesPropdriveFwd1: {
    yardTag: "45002080",
    componentType: SensorComponentType.PropulsionDrive,
  },
  drivesPropdriveFwd2: {
    yardTag: "45002080",
    componentType: SensorComponentType.PropulsionDrive,
  },
  drivesPump1: {
    yardTag: "50001028",
    componentType: SensorComponentType.Pump,
  },
  drivesPump2: {
    yardTag: "50001029",
    componentType: SensorComponentType.Pump,
  },
  drivesShorepower: {
    yardTag: "45002001",
    componentType: SensorComponentType.ShorePowerConverter,
  },
  drivesSwitchPropdriveAft1: {
    yardTag: "50001069-06",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchPropdriveAft2: {
    yardTag: "50001069-09",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchPropdriveFwd1: {
    yardTag: "50001069-07",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchPropdriveFwd2: {
    yardTag: "50001069-08",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchShorepowerReturn: {
    yardTag: "50001069-05",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesSwitchShorepowerSupply: {
    yardTag: "50001069-04",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  drivesTemperaturePropdriveAft1Return: {
    yardTag: "50001038-32",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperaturePropdriveAft2Return: {
    yardTag: "50001038-64",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperaturePropdriveFwd1Return: {
    yardTag: "50001038-61",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperaturePropdriveFwd2Return: {
    yardTag: "50001038-72",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperaturePropdrivesAftSupply: {
    yardTag: "50001038-63",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperaturePropdrivesFwdSupply: {
    yardTag: "50001038-62",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperatureRecovery: {
    yardTag: "50001038-16",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperatureRecoveryMix: {
    yardTag: "50001038-57",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperatureRecoveryReturn: {
    yardTag: "50001038-59",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperatureShorepowerReturn: {
    yardTag: "50001038-11",
    componentType: SensorComponentType.Temperature,
  },
  drivesTemperatureSupply: {
    yardTag: "50001038-14",
    componentType: SensorComponentType.Temperature,
  },
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
  },
});

export const DRIVES_SIMULATION_INPUTS = toSimulationDefinition({
  drivesDhwSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  drivesOilCoolerAft: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesOilCoolerFwd: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveAft1: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveAft2: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveFwd1: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveFwd2: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  drivesShorepower: {
    componentType: SimulationComponentType.HeatSource,
  },
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
});

export const DRIVES_SIMULATION_OUTPUTS = toSimulationDefinition({
  drivesDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  drivesSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});

export const HIGH_TEMPERATURE_SIMULATION_INPUTS = toSimulationDefinition({
  consumersAdsorptionSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  consumersDhwSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
  pcmFreshwaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtMainAft: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtMainFwd: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtOwners: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersPcs: {
    componentType: SimulationComponentType.Pcs,
  },
  thrustersSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersThrusterAft: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersThrusterFwd: {
    componentType: SimulationComponentType.Thruster,
  },
});

export const HIGH_TEMPERATURE_SIMULATION_OUTPUTS = toSimulationDefinition({
  consumersAdsorptionReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmConsumersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmFreshwaterReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmPvtReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmThrustersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtPcmSupply: {
    componentType: SimulationComponentType.Flow,
  },
  pvtSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  thrustersPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersPcmSupply: {
    componentType: SimulationComponentType.Flow,
  },
  thrustersSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});

export const PCM_CONTROL_DEFINITION = toControlDefinition({
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
  pcmModule1: {
    yardTag: "50001049",
    componentType: ControlComponentType.Pcm,
  },
  pcmPump: {
    yardTag: "50001017",
    componentType: ControlComponentType.Pump,
  },
  pcmSwitchChargingReturn: {
    yardTag: "50001062-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchChargingSupply: {
    yardTag: "50001190-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchConsumers: {
    yardTag: "50001071-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchDischarging: {
    yardTag: "50001066-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const PCM_CONTROLLER_STATE = toControllerStateDefinition({
  module1ChargeController: {
    componentType: ControllerStateComponentType.PcmChargeController,
  },
  module2ChargeController: {
    componentType: ControllerStateComponentType.PcmChargeController,
  },
  module3ChargeController: {
    componentType: ControllerStateComponentType.PcmChargeController,
  },
  module4ChargeController: {
    componentType: ControllerStateComponentType.PcmChargeController,
  },
  module1FlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  module2FlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  module3FlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  module4FlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
});

export const PCM_PARAMETER_DEFINITION = toParameterDefinition({
  chargingRequested: {
    componentType: ParametersType.Enabled,
  },
  gracePeriod: {
    componentType: ParametersType.Duration,
  },
  minimumChargingTemperature: {
    componentType: ParametersType.Temperature,
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
  pcmChargeFlow: {
    componentType: ParametersType.Flow,
  },
  pcmDischargeFlow: {
    componentType: ParametersType.Flow,
  },
  pumpTuning: {
    componentType: ParametersType.Tuning,
  },
  retryDelay: {
    componentType: ParametersType.Duration,
  },
  stallDuration: {
    componentType: ParametersType.Duration,
  },
  supplyingRequested: {
    componentType: ParametersType.Enabled,
  },
});

export const PCM_SENSOR_DEFINITION = toSensorDefinition({
  consumersFlowAdsorption: {
    yardTag: "50001058-08",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowBypass: {
    yardTag: "50001192",
    componentType: SensorComponentType.Flow,
  },
  consumersFlowDhw: {
    yardTag: "50001058-07",
    componentType: SensorComponentType.Flow,
  },
  consumersTemperatureAdsorptionReturn: {
    yardTag: "50001038-49",
    componentType: SensorComponentType.Temperature,
  },
  consumersTemperatureDhwReturn: {
    yardTag: "50001038-48",
    componentType: SensorComponentType.Temperature,
  },
  freshwaterFlowPcm: {
    yardTag: "25001139",
    componentType: SensorComponentType.FlowOnly,
  },
  freshwaterTemperaturePcmReturn: {
    yardTag: "25001038-3",
    componentType: SensorComponentType.Temperature,
  },
  freshwaterTemperaturePcmSupply: {
    yardTag: "25001038-5",
    componentType: SensorComponentType.Temperature,
  },
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
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
  pcmHeatModule1: {
    yardTag: "50001049",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pcmHeatModule1Freshwater: {
    yardTag: "50001049",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pcmHeatModule2: {
    yardTag: "50001050",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pcmHeatModule3: {
    yardTag: "50001051",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pcmHeatModule4: {
    yardTag: "50001052",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pcmPump: {
    yardTag: "50001017",
    componentType: SensorComponentType.Pump,
  },
  pcmSwitchChargingReturn: {
    yardTag: "50001062-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchChargingSupply: {
    yardTag: "50001190-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchConsumers: {
    yardTag: "50001071-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmSwitchDischarging: {
    yardTag: "50001066-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pcmTemperatureConsumersReturn: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pcmTemperatureModule1: {
    yardTag: "50001038-60",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule2: {
    yardTag: "50001038-33",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule3: {
    yardTag: "50001038-34",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureModule4: {
    yardTag: "50001038-35",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureProducersReturn: {
    yardTag: "50001038-31",
    componentType: SensorComponentType.Temperature,
  },
  pcmTemperatureProducersSupply: {
    yardTag: "50001038-55",
    componentType: SensorComponentType.Temperature,
  },
});

export const PCM_SIMULATION_INPUTS = toSimulationDefinition({
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
  pcmConsumersSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  pcmFreshwaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmPvtSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmThrustersSupply: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const PCM_SIMULATION_OUTPUTS = toSimulationDefinition({
  pcmConsumersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmFreshwaterReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmPvtReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmThrustersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const PVT_CONTROL_DEFINITION = toControlDefinition({
  pvtMixExchanger: {
    yardTag: "50001047-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixMainAft: {
    yardTag: "50001044-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixMainFwd: {
    yardTag: "50001044-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixOwners: {
    yardTag: "50001043-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtPumpMainAft: {
    yardTag: "50001019",
    componentType: ControlComponentType.Pump,
  },
  pvtPumpMainFwd: {
    yardTag: "50001018",
    componentType: ControlComponentType.Pump,
  },
  pvtPumpOwners: {
    yardTag: "50001021",
    componentType: ControlComponentType.Pump,
  },
  pvtSwitchMainAft: {
    yardTag: "50001067-02",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchMainFwd: {
    yardTag: "50001067-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchOwners: {
    yardTag: "50001069-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const PVT_CONTROLLER_STATE = toControllerStateDefinition({
  pvtHeatDumpController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  pvtMainAftPumpController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  pvtMainAftWarmupMixController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  pvtMainFwdPumpController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  pvtMainFwdWarmupMixController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  pvtOwnersPumpController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  pvtOwnersWarmupMixController: {
    componentType: ControllerStateComponentType.PIDController,
  },
});

export const PVT_PARAMETER_DEFINITION = toParameterDefinition({
  heatDumpTuning: {
    componentType: ParametersType.Tuning,
  },
  mainAftMinimumPumpDutypoint: {
    componentType: ParametersType.Dutypoint,
  },
  mainAftMixTuning: {
    componentType: ParametersType.Tuning,
  },
  mainAftPumpTuning: {
    componentType: ParametersType.Tuning,
  },
  mainFwdMinimumPumpDutypoint: {
    componentType: ParametersType.Dutypoint,
  },
  mainFwdMixTuning: {
    componentType: ParametersType.Tuning,
  },
  mainFwdPumpTuning: {
    componentType: ParametersType.Tuning,
  },
  maximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
  minimumReturnTemperature: {
    componentType: ParametersType.Temperature,
  },
  ownersMinimumPumpDutypoint: {
    componentType: ParametersType.Dutypoint,
  },
  ownersMixTuning: {
    componentType: ParametersType.Tuning,
  },
  ownersPumpTuning: {
    componentType: ParametersType.Tuning,
  },
  recoveryActivationStringTemperature: {
    componentType: ParametersType.Temperature,
  },
  recoveryTemperature: {
    componentType: ParametersType.Temperature,
  },
  warmupTemperature: {
    componentType: ParametersType.Temperature,
  },
});

export const PVT_SENSOR_DEFINITION = toSensorDefinition({
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
  },
  pcmTemperatureProducersSupply: {
    yardTag: "50001038-55",
    componentType: SensorComponentType.Temperature,
  },
  pvtFlowMainAftRecovery: {
    yardTag: "50001058-13",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainAftStrings: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  pvtFlowMainFwdRecovery: {
    yardTag: "50001058-12",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainFwdStrings: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  pvtFlowMainString10: {
    yardTag: "50009009-04",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString11: {
    yardTag: "50009006-01",
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
  pvtFlowMainString12: {
    yardTag: "50009009-05",
    componentType: SensorComponentType.Flow,
  },
  pvtFlowMainString13: {
    yardTag: "50009009-06",
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
  pvtFlowOwnersRecovery: {
    yardTag: "50001057-03",
    componentType: SensorComponentType.Flow,
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
  pvtFlowOwnersStrings: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  pvtMaxTemperatureMainAftStrings: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtMaxTemperatureMainFwdStrings: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtMaxTemperatureOwnersStrings: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtMixExchanger: {
    yardTag: "50001047-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixMainAft: {
    yardTag: "50001044-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixMainFwd: {
    yardTag: "50001044-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtMixOwners: {
    yardTag: "50001043-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  pvtPressureMainAft: {
    yardTag: "50001097-04",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureMainFwd: {
    yardTag: "50001097-03",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureMainVacuum: {
    yardTag: "50009059-01",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureOwners: {
    yardTag: "50001097-05",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureOwnersVacuum: {
    yardTag: "50009059-02",
    componentType: SensorComponentType.Pressure,
  },
  pvtPressureSystem: {
    yardTag: "50001097-06",
    componentType: SensorComponentType.Pressure,
  },
  pvtPumpMainAft: {
    yardTag: "50001019",
    componentType: SensorComponentType.Pump,
  },
  pvtPumpMainFwd: {
    yardTag: "50001018",
    componentType: SensorComponentType.Pump,
  },
  pvtPumpOwners: {
    yardTag: "50001021",
    componentType: SensorComponentType.Pump,
  },
  pvtPvtMainAft: {
    yardTag: "50009002-01",
    componentType: SensorComponentType.Pvt,
  },
  pvtPvtMainAftHeat: {
    yardTag: "50009002-01",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pvtPvtMainFwd: {
    yardTag: "50009001-01",
    componentType: SensorComponentType.Pvt,
  },
  pvtPvtMainFwdHeat: {
    yardTag: "50009001-01",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pvtPvtOwners: {
    yardTag: "50009001-03",
    componentType: SensorComponentType.Pvt,
  },
  pvtPvtOwnersHeat: {
    yardTag: "50009001-03",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pvtPyranometerPs: {
    yardTag: "50009043",
    componentType: SensorComponentType.Pyranometer,
  },
  pvtPyranometerSb: {
    yardTag: "50009044",
    componentType: SensorComponentType.Pyranometer,
  },
  pvtReturnTemperature: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtSeawaterExchanger: {
    yardTag: "50001002",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  pvtSeawaterExchangerFlow: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  pvtSwitchMainAft: {
    yardTag: "50001067-02",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchMainFwd: {
    yardTag: "50001067-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtSwitchOwners: {
    yardTag: "50001069-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  pvtTemperatureMainAftReturn: {
    yardTag: "50001038-73",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainAftStringsReturn: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtTemperatureMainAftStringsSupply: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtTemperatureMainAftSupply: {
    yardTag: "50001038-22",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainFwdReturn: {
    yardTag: "50001038-03",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainFwdStringsReturn: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtTemperatureMainFwdStringsSupply: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtTemperatureMainFwdSupply: {
    yardTag: "50001038-23",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString10Return: {
    yardTag: "50009005-16",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString10Supply: {
    yardTag: "50009005-30",
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
  pvtTemperatureMainString11Return: {
    yardTag: "50009005-01",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString11Supply: {
    yardTag: "50009005-31",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString12Return: {
    yardTag: "50009005-19",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString12Supply: {
    yardTag: "50009005-32",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString13Return: {
    yardTag: "50009005-20",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString13Supply: {
    yardTag: "50009005-33",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString1Supply: {
    yardTag: "50009005-26",
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
  pvtTemperatureMainString2Supply: {
    yardTag: "50009005-25",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString3Return: {
    yardTag: "50009005-05",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString3Supply: {
    yardTag: "50009005-24",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString4Return: {
    yardTag: "50009005-06",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString4Supply: {
    yardTag: "50009005-23",
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
  pvtTemperatureMainString5Supply: {
    yardTag: "50009005-22",
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
  pvtTemperatureMainString7Supply: {
    yardTag: "50009005-27",
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
  pvtTemperatureMainString8Supply: {
    yardTag: "50009005-28",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString9Return: {
    yardTag: "50009005-15",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureMainString9Supply: {
    yardTag: "50009005-29",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersReturn: {
    yardTag: "50001038-04",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString1Return: {
    yardTag: "50009005-34",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString1Supply: {
    yardTag: "50009005-40",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString2Return: {
    yardTag: "50009005-35",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString2Supply: {
    yardTag: "50009005-41",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString3Return: {
    yardTag: "50009005-36",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString3Supply: {
    yardTag: "50009005-42",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString4Return: {
    yardTag: "50009005-37",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString4Supply: {
    yardTag: "50009005-43",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString5Return: {
    yardTag: "50009005-38",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString5Supply: {
    yardTag: "50009005-44",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString6Return: {
    yardTag: "50009005-39",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersString6Supply: {
    yardTag: "50009005-45",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureOwnersStringsReturn: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtTemperatureOwnersStringsSupply: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  pvtTemperatureOwnersSupply: {
    yardTag: "50001038-21",
    componentType: SensorComponentType.Temperature,
  },
  pvtTemperatureSupply: {
    yardTag: "50001038-24",
    componentType: SensorComponentType.Temperature,
  },
  pvtTotalFlow: {
    componentType: SensorComponentType.CalculatedFlow,
  },
});

export const PVT_SIMULATION_INPUTS = toSimulationDefinition({
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
  pvtMainAft: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtMainFwd: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtOwners: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtPcmSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  pvtSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
});

export const PVT_SIMULATION_OUTPUTS = toSimulationDefinition({
  pvtPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtPcmSupply: {
    componentType: SimulationComponentType.Flow,
  },
  pvtSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});

export const THRS_SIMULATION_INPUTS = toSimulationDefinition({
  adsorptionAvailableColdTemperature: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionAvailableHotTemperature: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionAvailableSeawaterTemperature: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionChiller: {
    componentType: SimulationComponentType.AdsorptionChiller,
  },
  adsorptionCoolingSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dcBrightloopAft1: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopAft2: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopAft3: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopAft4: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopFwd1: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcBrightloopFwd2: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dcUgrid1: {
    componentType: SimulationComponentType.HeatSource,
  },
  dcUgrid2: {
    componentType: SimulationComponentType.HeatSource,
  },
  dhwFreshwaterSupply: {
    componentType: SimulationComponentType.OverpressureTemperature,
  },
  dhwHotwaterDemand: {
    componentType: SimulationComponentType.Flow,
  },
  dhwHvacExchanger: {
    componentType: SimulationComponentType.HvacExchanger,
  },
  dhwSeawaterSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  drivesOilCoolerAft: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesOilCoolerFwd: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveAft1: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveAft2: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveFwd1: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesPropdriveFwd2: {
    componentType: SimulationComponentType.HeatSource,
  },
  drivesSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  drivesShorepower: {
    componentType: SimulationComponentType.HeatSource,
  },
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
  pcmFreshwaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtMainAft: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtMainFwd: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtOwners: {
    componentType: SimulationComponentType.HeatSource,
  },
  pvtSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersPcs: {
    componentType: SimulationComponentType.Pcs,
  },
  thrustersSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersThrusterAft: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersThrusterFwd: {
    componentType: SimulationComponentType.Thruster,
  },
});

export const THRS_SIMULATION_OUTPUTS = toSimulationDefinition({
  adsorptionConsumersReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionCoolingReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  adsorptionDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  adsorptionSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersAdsorptionReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  consumersPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  dcDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dcSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwAdsorptionReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwConsumersReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwDcReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwDrivesReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwFreshwaterReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  dhwSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  dhwSeawaterSupply: {
    componentType: SimulationComponentType.Flow,
  },
  drivesDhwReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  drivesSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  pcmConsumersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmFreshwaterReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmPvtReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pcmThrustersReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  pvtPcmSupply: {
    componentType: SimulationComponentType.Flow,
  },
  pvtSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
  thrustersPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersPcmSupply: {
    componentType: SimulationComponentType.Flow,
  },
  thrustersSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});

export const THRUSTERS_CONTROL_DEFINITION = toControlDefinition({
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
  thrustersMixExchanger: {
    yardTag: "50001214-01",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersMixRecovery: {
    yardTag: "50001074",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersPump1: {
    yardTag: "50001194",
    componentType: ControlComponentType.Pump,
  },
  thrustersPump2: {
    yardTag: "50001195",
    componentType: ControlComponentType.Pump,
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
  thrustersSwitchRecovery: {
    yardTag: "50001066-03",
    componentType: ControlComponentType.Valve,
    valveType: ValveType.Switch,
  },
});

export const THRUSTERS_CONTROLLER_STATE = toControllerStateDefinition({
  thrustersAftFlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  thrustersAftRecoveryTemperatureController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  thrustersFwdFlowController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  thrustersFwdRecoveryTemperatureController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  thrustersHeatDumpController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  thrustersPumpController: {
    componentType: ControllerStateComponentType.PIDController,
  },
  thrustersWarmupMixController: {
    componentType: ControllerStateComponentType.PIDController,
  },
});

export const THRUSTERS_PARAMETER_DEFINITION = toParameterDefinition({
  aftFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  aftTemperatureTuning: {
    componentType: ParametersType.Tuning,
  },
  coolingFlow: {
    componentType: ParametersType.Flow,
  },
  coolingTemperature: {
    componentType: ParametersType.Temperature,
  },
  fwdFlowBalanceTuning: {
    componentType: ParametersType.Tuning,
  },
  fwdTemperatureTuning: {
    componentType: ParametersType.Tuning,
  },
  heatDumpTuning: {
    componentType: ParametersType.Tuning,
  },
  maximumSupplyTemperature: {
    componentType: ParametersType.Temperature,
  },
  pumpTuning: {
    componentType: ParametersType.Tuning,
  },
  recoveryTemperature: {
    componentType: ParametersType.Temperature,
  },
  thrustersMaximumFlow: {
    componentType: ParametersType.Flow,
  },
  thrustersMinimumFlow: {
    componentType: ParametersType.Flow,
  },
  warmupMixTuning: {
    componentType: ParametersType.Tuning,
  },
  warmupTemperature: {
    componentType: ParametersType.Temperature,
  },
});

export const THRUSTERS_SENSOR_DEFINITION = toSensorDefinition({
  mode: {
    componentType: SensorComponentType.AmcsControlMode,
  },
  thrustersFlow: {
    componentType: SensorComponentType.CalculatedFlow,
  },
  thrustersFlowAft: {
    yardTag: "50001218-02",
    componentType: SensorComponentType.Flow,
  },
  thrustersFlowFwd: {
    yardTag: "50001057-22",
    componentType: SensorComponentType.Flow,
  },
  thrustersFlowRecovery: {
    yardTag: "50001218-01",
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
  thrustersMixExchanger: {
    yardTag: "50001214-01",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersMixRecovery: {
    yardTag: "50001074",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Mix,
  },
  thrustersPcs: {
    yardTag: "1500",
    componentType: SensorComponentType.Pcs,
  },
  thrustersPressureDischarge: {
    yardTag: "50001097-01",
    componentType: SensorComponentType.Pressure,
  },
  thrustersPressureSystem: {
    yardTag: "50001097-02",
    componentType: SensorComponentType.Pressure,
  },
  thrustersPump1: {
    yardTag: "50001194",
    componentType: SensorComponentType.Pump,
  },
  thrustersPump2: {
    yardTag: "50001195",
    componentType: SensorComponentType.Pump,
  },
  thrustersSeawaterExchanger: {
    yardTag: "50001001",
    componentType: SensorComponentType.HeatTransferDevice,
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
  thrustersSwitchRecovery: {
    yardTag: "50001066-03",
    componentType: SensorComponentType.Valve,
    valveType: ValveType.Switch,
  },
  thrustersTemperatureAft: {
    yardTag: "50001038-01",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureFwd: {
    yardTag: "50001038-02",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperaturePreCooler: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  thrustersTemperatureRecovery: {
    componentType: SensorComponentType.CalculatedTemperature,
  },
  thrustersTemperatureRecoveryMix: {
    yardTag: "50001038-30",
    componentType: SensorComponentType.Temperature,
  },
  thrustersTemperatureSupply: {
    yardTag: "50001038-28",
    componentType: SensorComponentType.Temperature,
  },
  thrustersThrusterAft: {
    yardTag: "15001001",
    componentType: SensorComponentType.Thruster,
  },
  thrustersThrusterAftHeat: {
    yardTag: "15001001",
    componentType: SensorComponentType.HeatTransferDevice,
  },
  thrustersThrusterFwd: {
    yardTag: "15001002",
    componentType: SensorComponentType.Thruster,
  },
  thrustersThrusterFwdHeat: {
    yardTag: "15001002",
    componentType: SensorComponentType.HeatTransferDevice,
  },
});

export const THRUSTERS_SIMULATION_INPUTS = toSimulationDefinition({
  mode: {
    componentType: SimulationComponentType.AmcsControlMode,
  },
  thrustersPcmSupply: {
    componentType: SimulationComponentType.Temperature,
  },
  thrustersPcs: {
    componentType: SimulationComponentType.Pcs,
  },
  thrustersSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersThrusterAft: {
    componentType: SimulationComponentType.Thruster,
  },
  thrustersThrusterFwd: {
    componentType: SimulationComponentType.Thruster,
  },
});

export const THRUSTERS_SIMULATION_OUTPUTS = toSimulationDefinition({
  thrustersPcmReturn: {
    componentType: SimulationComponentType.Boundary,
  },
  thrustersPcmSupply: {
    componentType: SimulationComponentType.Flow,
  },
  thrustersSeawaterReturn: {
    componentType: SimulationComponentType.Temperature,
  },
});
