export const DHW_CONTROL_QUERY = `
  dhwPump {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  dhwHeatpump {
    temperatureSetpoint { value timestamp }
    on { value timestamp }
  }
  dhwFlowcontrolDc {
    setpoint { value timestamp }
  }
  dhwFlowcontrolDrives {
    setpoint { value timestamp }
  }
  dhwSwitchTank3Inlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank3BoostingReturn {
    setpoint { value timestamp }
  }
  dhwSwitchTank3Outlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank3BoostingSupply {
    setpoint { value timestamp }
  }
  dhwSwitchTank2Inlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank2BoostingReturn {
    setpoint { value timestamp }
  }
  dhwSwitchTank2Outlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank2BoostingSupply {
    setpoint { value timestamp }
  }
  dhwSwitchTank1Inlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank1BoostingReturn {
    setpoint { value timestamp }
  }
  dhwSwitchTank1Outlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank1BoostingSupply {
    setpoint { value timestamp }
  }
  dhwSwitchLowTemperature {
    setpoint { value timestamp }
  }
  dhwSwitchHeatpump {
    setpoint { value timestamp }
  }
  dhwSwitchHighTemperature {
    setpoint { value timestamp }
  }
  dhwTanksController {
    tank1State { value timestamp }
    tank2State { value timestamp }
    tank3State { value timestamp }
    timeToFill { value timestamp }
  }
  dhwPumpFlowController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  dhwPumpTemperatureController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  dhwDrivesFlowController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  dhwDcFlowController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
`;

export const DHW_PARAMETERS_QUERY = `
  heatpumpFlowSetpoint
  heatpumpTemperatureSetpoint
  htBoostingTemperatureSetpoint
  minimumTankTemperature
  maximumTankTemperature
  boostingDelta
  drivesFlowcontrolMinimumSetpoint
  dcFlowcontrolMinimumSetpoint
  fillingTemperatureSetpoint
  minimumTankLevel
  maximumTankLevel
  tank1Disabled
  tank2Disabled
  tank3Disabled
  pumpTemperatureTuning
  pumpFlowTuning
  dcFlowTuning
  drivesFlowTuning
`;

export const DHW_SENSOR_QUERY = `
  dhwPump {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
  }
  dhwTemperatureHvacExchangerReturn {
    temperature { value timestamp }
  }
  dhwTemperatureDcReturn {
    temperature { value timestamp }
  }
  dhwTemperatureTank3 {
    temperature { value timestamp }
  }
  dhwTemperatureTank2 {
    temperature { value timestamp }
  }
  dhwTemperatureTank1 {
    temperature { value timestamp }
  }
  dhwTemperatureDrivesReturn {
    temperature { value timestamp }
  }
  dhwTemperatureFreshwaterSupply {
    temperature { value timestamp }
  }
  dhwTemperatureAdsorptionReturn {
    temperature { value timestamp }
  }
  dhwTemperatureBoostingReturn {
    temperature { value timestamp }
  }
  dhwTemperatureBoostingSupply {
    temperature { value timestamp }
  }
  dhwLevelTank1 {
    level { value timestamp }
  }
  dhwLevelTank2 {
    level { value timestamp }
  }
  dhwLevelTank3 {
    level { value timestamp }
  }
  dhwFlowDc {
    flow { value timestamp }
    temperature { value timestamp }
  }
  dhwFlowDrives {
    flow { value timestamp }
    temperature { value timestamp }
  }
  dhwFlowBoosting {
    flow { value timestamp }
    temperature { value timestamp }
  }
  dhwFlowcontrolDc {
    positionRel { value timestamp }
  }
  dhwFlowcontrolDrives {
    positionRel { value timestamp }
  }
  dhwSwitchTank3Inlet {
    positionRel { value timestamp }
  }
  dhwSwitchTank3BoostingReturn {
    positionRel { value timestamp }
  }
  dhwSwitchTank3Outlet {
    positionRel { value timestamp }
  }
  dhwSwitchTank3BoostingSupply {
    positionRel { value timestamp }
  }
  dhwSwitchTank2Inlet {
    positionRel { value timestamp }
  }
  dhwSwitchTank2BoostingReturn {
    positionRel { value timestamp }
  }
  dhwSwitchTank2Outlet {
    positionRel { value timestamp }
  }
  dhwSwitchTank2BoostingSupply {
    positionRel { value timestamp }
  }
  dhwSwitchTank1Inlet {
    positionRel { value timestamp }
  }
  dhwSwitchTank1BoostingReturn {
    positionRel { value timestamp }
  }
  dhwSwitchTank1Outlet {
    positionRel { value timestamp }
  }
  dhwSwitchTank1BoostingSupply {
    positionRel { value timestamp }
  }
  dhwSwitchLowTemperature {
    positionRel { value timestamp }
  }
  dhwSwitchHeatpump {
    positionRel { value timestamp }
  }
  dhwSwitchHighTemperature {
    positionRel { value timestamp }
  }
  dhwPressure {
    pressure { value timestamp }
  }
  drivesFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
  }
  drivesTemperatureRecovery {
    temperature { value timestamp }
  }
  drivesTemperatureRecoveryReturn {
    temperature { value timestamp }
  }
  dcFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
  }
  dcTemperatureRecovery {
    temperature { value timestamp }
  }
  dcTemperatureRecoveryReturn {
    temperature { value timestamp }
  }
  consumersFlowDhw {
    flow { value timestamp }
    temperature { value timestamp }
  }
  consumersTemperatureDhwSupply {
    temperature { value timestamp }
  }
  consumersTemperatureDhwReturn {
    temperature { value timestamp }
  }
  adsorptionFlowDhw {
    flow { value timestamp }
    temperature { value timestamp }
  }
  adsorptionTemperatureWasteReturn {
    temperature { value timestamp }
  }
  adsorptionTemperatureDhwReturn {
    temperature { value timestamp }
  }
  freshwaterHotwaterFlow {
    flow { value timestamp }
    temperature { value timestamp }
  }
  freshwaterHotwaterTemperature {
    temperature { value timestamp }
  }
  drivesDelta {
    deltaT { value timestamp }
  }
  dcDelta {
    deltaT { value timestamp }
  }
  consumersDelta {
    deltaT { value timestamp }
  }
  adsorptionDelta {
    deltaT { value timestamp }
  }
  freshwaterFlowSupply {
    flow { value timestamp }
  }
  dhwHvacExchanger {
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwHeatpump {
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwFahrenheitExchanger {
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwConsumersExchanger {
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwDcExchanger {
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwDrivesExchanger {
    heat { value timestamp }
    deltaT { value timestamp }
  }
`;

export const DHW_SIMULATION_INPUTS_QUERY = `
  dhwDrivesSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwDcSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwAdsorptionSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwHtSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwFreshwaterSupply {
    temperature { value timestamp }
    overpressure { value timestamp }
  }
  dhwSeawaterSupply {
    temperature { value timestamp }
  }
  dhwHotwaterDemand {
    flow { value timestamp }
  }
`;

export const DHW_SIMULATION_OUTPUTS_QUERY = `
  dhwDrivesReturn {
    temperature { value timestamp }
  }
  dhwDcReturn {
    temperature { value timestamp }
  }
  dhwAdsorptionReturn {
    temperature { value timestamp }
  }
  dhwHtReturn {
    temperature { value timestamp }
  }
  dhwSeawaterReturn {
    temperature { value timestamp }
  }
  dhwSeawaterSupply {
    flow { value timestamp }
  }
  dhwFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const CONSUMERS_CONTROL_QUERY = `
  consumersFlowcontrolAdsorption {
    setpoint { value timestamp }
  }
  consumersFlowcontrolBypass {
    setpoint { value timestamp }
  }
  consumersFlowcontrolDhw {
    setpoint { value timestamp }
  }
  consumersSwitchAdsorption {
    setpoint { value timestamp }
  }
  consumersSwitchDhw {
    setpoint { value timestamp }
  }
`;

export const CONSUMERS_PARAMETERS_QUERY = `
  dhwEnabled
  dhwFlowRatioSetpoint
  adsorptionEnabled
  adsorptionFlowRatioSetpoint
  dhwFlowBalanceTuning
  bypassFlowBalanceTuning
  adsorptionFlowBalanceTuning
`;

export const CONSUMERS_SENSOR_QUERY = `
  consumersTemperatureDhwReturn {
    temperature { value timestamp }
  }
  consumersTemperatureAdsorptionReturn {
    temperature { value timestamp }
  }
  consumersTemperatureDhwSupply {
    temperature { value timestamp }
  }
  consumersTemperatureAdsorptionSupply {
    temperature { value timestamp }
  }
  consumersFlowDhw {
    flow { value timestamp }
    temperature { value timestamp }
  }
  consumersFlowAdsorption {
    flow { value timestamp }
    temperature { value timestamp }
  }
  consumersFlowBypass {
    flow { value timestamp }
    temperature { value timestamp }
  }
  consumersFlowcontrolAdsorption {
    positionRel { value timestamp }
  }
  consumersFlowcontrolBypass {
    positionRel { value timestamp }
  }
  consumersFlowcontrolDhw {
    positionRel { value timestamp }
  }
  consumersSwitchAdsorption {
    positionRel { value timestamp }
  }
  consumersSwitchDhw {
    positionRel { value timestamp }
  }
`;

export const CONSUMERS_SIMULATION_INPUTS_QUERY = `
  consumersAdsorptionSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersDhwSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersPcmSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const CONSUMERS_SIMULATION_OUTPUTS_QUERY = `
  consumersAdsorptionReturn {
    temperature { value timestamp }
  }
  consumersDhwReturn {
    temperature { value timestamp }
  }
  consumersPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY = `
  thrustersThrusterAft {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
  pvtMainFwd {
    heatFlow { value timestamp }
  }
  pvtMainAft {
    heatFlow { value timestamp }
  }
  pvtOwners {
    heatFlow { value timestamp }
  }
  pvtSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmFreshwaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersDhwSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersAdsorptionSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY = `
  thrustersSeawaterReturn {
    temperature { value timestamp }
  }
  thrustersPcmSupply {
    flow { value timestamp }
  }
  thrustersPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pvtPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pvtPcmSupply {
    flow { value timestamp }
  }
  pvtSeawaterReturn {
    temperature { value timestamp }
  }
  consumersAdsorptionReturn {
    temperature { value timestamp }
  }
  consumersDhwReturn {
    temperature { value timestamp }
  }
  consumersPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmConsumersReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmPvtReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const PCM_CONTROL_QUERY = `
  pcmPump {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pcmSwitchChargingReturn {
    setpoint { value timestamp }
  }
  pcmFlowcontrolModule1 {
    setpoint { value timestamp }
  }
  pcmFlowcontrolModule2 {
    setpoint { value timestamp }
  }
  pcmFlowcontrolModule3 {
    setpoint { value timestamp }
  }
  pcmFlowcontrolModule4 {
    setpoint { value timestamp }
  }
  pcmSwitchDischarging {
    setpoint { value timestamp }
  }
  pcmSwitchChargingSupply {
    setpoint { value timestamp }
  }
  pcmSwitchConsumers {
    setpoint { value timestamp }
  }
  pcmModule1 {
    on { value timestamp }
  }
`;

export const PCM_PARAMETERS_QUERY = `
  pcmDischargeFlow
  pcmChargeFlow
  minimumChargingDt
  minimumChargingTemperature
  pumpTuning
  supplyingEnabled
  chargingEnabled
  module1FlowBalanceTuning
  module2FlowBalanceTuning
  module3FlowBalanceTuning
  module4FlowBalanceTuning
`;

export const PCM_SENSOR_QUERY = `
  pcmPump {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
  }
  pcmTemperatureProducersReturn {
    temperature { value timestamp }
  }
  pcmTemperatureProducersSupply {
    temperature { value timestamp }
  }
  pcmTemperatureModule1 {
    temperature { value timestamp }
  }
  pcmTemperatureModule2 {
    temperature { value timestamp }
  }
  pcmTemperatureModule3 {
    temperature { value timestamp }
  }
  pcmTemperatureModule4 {
    temperature { value timestamp }
  }
  pcmModule1 {
    charged { value timestamp }
  }
  pcmModule2 {
    charged { value timestamp }
  }
  pcmModule3 {
    charged { value timestamp }
  }
  pcmModule4 {
    charged { value timestamp }
  }
  pcmFlowModule1 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pcmFlowModule2 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pcmFlowModule3 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pcmFlowModule4 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pcmSwitchChargingReturn {
    positionRel { value timestamp }
  }
  pcmFlowcontrolModule1 {
    positionRel { value timestamp }
  }
  pcmFlowcontrolModule2 {
    positionRel { value timestamp }
  }
  pcmFlowcontrolModule3 {
    positionRel { value timestamp }
  }
  pcmFlowcontrolModule4 {
    positionRel { value timestamp }
  }
  pcmSwitchDischarging {
    positionRel { value timestamp }
  }
  pcmSwitchChargingSupply {
    positionRel { value timestamp }
  }
  pcmSwitchConsumers {
    positionRel { value timestamp }
  }
`;

export const PCM_SIMULATION_INPUTS_QUERY = `
  pcmThrustersSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmConsumersSupply {
    temperature { value timestamp }
  }
  pcmFreshwaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const PCM_SIMULATION_OUTPUTS_QUERY = `
  pcmConsumersReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmPvtReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const PVT_CONTROL_QUERY = `
  pvtPumpMainFwd {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pvtPumpMainAft {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pvtPumpOwners {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pvtMixMainFwd {
    setpoint { value timestamp }
  }
  pvtMixMainAft {
    setpoint { value timestamp }
  }
  pvtMixOwners {
    setpoint { value timestamp }
  }
  pvtSwitchMainFwd {
    setpoint { value timestamp }
  }
  pvtSwitchMainAft {
    setpoint { value timestamp }
  }
  pvtSwitchOwners {
    setpoint { value timestamp }
  }
  pvtMixExchanger {
    setpoint { value timestamp }
  }
`;

export const PVT_PARAMETERS_QUERY = `
  maximumSupplyTemperature
  recoveryTemperature
  warmupTemperature
  recoveryActivationStringTemperature
  minimumReturnTemperature
  mainFwdMinimumPumpDutypoint
  mainAftMinimumPumpDutypoint
  ownersMinimumPumpDutypoint
  heatDumpTuning
  mainFwdMixTuning
  mainAftMixTuning
  ownersMixTuning
  mainFwdPumpTuning
  mainAftPumpTuning
  ownersPumpTuning
`;

export const PVT_SENSOR_QUERY = `
  pvtPumpMainFwd {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
  }
  pvtPumpMainAft {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
  }
  pvtPumpOwners {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
  }
  pvtTemperatureMainFwdReturn {
    temperature { value timestamp }
  }
  pvtTemperatureMainFwdSupply {
    temperature { value timestamp }
  }
  pvtTemperatureMainAftReturn {
    temperature { value timestamp }
  }
  pvtTemperatureMainAftSupply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersSupply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersReturn {
    temperature { value timestamp }
  }
  pvtMixMainFwd {
    positionRel { value timestamp }
  }
  pvtMixMainAft {
    positionRel { value timestamp }
  }
  pvtMixOwners {
    positionRel { value timestamp }
  }
  pvtFlowMainFwdRecovery {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainAftRecovery {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowOwnersRecovery {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtPressureMainFwd {
    pressure { value timestamp }
  }
  pvtPressureMainAft {
    pressure { value timestamp }
  }
  pvtPressureOwners {
    pressure { value timestamp }
  }
  pvtPressureSystem {
    pressure { value timestamp }
  }
  pvtSwitchMainFwd {
    positionRel { value timestamp }
  }
  pvtSwitchMainAft {
    positionRel { value timestamp }
  }
  pvtSwitchOwners {
    positionRel { value timestamp }
  }
  pvtMixExchanger {
    positionRel { value timestamp }
  }
  pvtTemperatureSupply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString11Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString12Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString21Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString22Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString3Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString4Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString51Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString52Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString61Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString62Return {
    temperature { value timestamp }
  }
  pvtFlowMainString11 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString12 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString21 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString22 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString3 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString4 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString51 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString52 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString61 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString62 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtTemperatureMainString1Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString2Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString3Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString4Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString5Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString6Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString71Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString72Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString81Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString82Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString9Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString10Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString111Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString112Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString13Return {
    temperature { value timestamp }
  }
  pvtFlowMainString71 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString72 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString81 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString82 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString9 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString10 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString111 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString112 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowMainString13 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtTemperatureMainString7Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString8Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString9Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString10Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString11Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString12Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString13Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString1Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString2Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString3Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString4Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString5Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString6Return {
    temperature { value timestamp }
  }
  pvtFlowOwnersString1 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowOwnersString2 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowOwnersString3 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowOwnersString4 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowOwnersString5 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtFlowOwnersString6 {
    flow { value timestamp }
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString1Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString2Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString3Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString4Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString5Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString6Supply {
    temperature { value timestamp }
  }
`;

export const PVT_SIMULATION_INPUTS_QUERY = `
  pvtMainFwd {
    heatFlow { value timestamp }
  }
  pvtMainAft {
    heatFlow { value timestamp }
  }
  pvtOwners {
    heatFlow { value timestamp }
  }
  pvtPcmSupply {
    temperature { value timestamp }
  }
  pvtSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const PVT_SIMULATION_OUTPUTS_QUERY = `
  pvtPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pvtPcmSupply {
    flow { value timestamp }
  }
  pvtSeawaterReturn {
    temperature { value timestamp }
  }
`;

export const THRUSTERS_CONTROL_QUERY = `
  thrustersPump1 {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  thrustersPump2 {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  thrustersMixRecovery {
    setpoint { value timestamp }
  }
  thrustersMixExchanger {
    setpoint { value timestamp }
  }
  thrustersFlowcontrolAft {
    setpoint { value timestamp }
  }
  thrustersFlowcontrolFwd {
    setpoint { value timestamp }
  }
  thrustersSwitchRecovery {
    setpoint { value timestamp }
  }
  thrustersSwitchAft {
    setpoint { value timestamp }
  }
  thrustersSwitchFwd {
    setpoint { value timestamp }
  }
`;

export const THRUSTERS_PARAMETERS_QUERY = `
  maximumSupplyTemperature
  coolingTemperature
  coolingFlow
  recoveryTemperature
  warmupTemperature
  thrustersMinimumFlow
  thrustersMaximumFlow
  pumpTuning
  warmupMixTuning
  heatDumpTuning
  aftFlowBalanceTuning
  fwdFlowBalanceTuning
  aftTemperatureTuning
  fwdTemperatureTuning
`;

export const THRUSTERS_SENSOR_QUERY = `
  thrustersPump1 {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
  }
  thrustersPump2 {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
  }
  thrustersTemperatureAft {
    temperature { value timestamp }
  }
  thrustersTemperatureFwd {
    temperature { value timestamp }
  }
  thrustersTemperatureSupply {
    temperature { value timestamp }
  }
  thrustersTemperatureRecoveryMix {
    temperature { value timestamp }
  }
  thrustersMixRecovery {
    positionRel { value timestamp }
  }
  thrustersMixExchanger {
    positionRel { value timestamp }
  }
  thrustersFlowFwd {
    flow { value timestamp }
    temperature { value timestamp }
  }
  thrustersFlowAft {
    flow { value timestamp }
    temperature { value timestamp }
  }
  thrustersFlowcontrolAft {
    positionRel { value timestamp }
  }
  thrustersFlowcontrolFwd {
    positionRel { value timestamp }
  }
  thrustersSwitchRecovery {
    positionRel { value timestamp }
  }
  thrustersSwitchAft {
    positionRel { value timestamp }
  }
  thrustersSwitchFwd {
    positionRel { value timestamp }
  }
  thrustersFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
  }
  thrustersPressureDischarge {
    pressure { value timestamp }
  }
  thrustersPressureSystem {
    pressure { value timestamp }
  }
  thrustersThrusterAft {
    active { value timestamp }
  }
  thrustersThrusterFwd {
    active { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
`;

export const THRUSTERS_SIMULATION_INPUTS_QUERY = `
  thrustersThrusterAft {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersPcmSupply {
    temperature { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
`;

export const THRUSTERS_SIMULATION_OUTPUTS_QUERY = `
  thrustersSeawaterReturn {
    temperature { value timestamp }
  }
  thrustersPcmSupply {
    flow { value timestamp }
  }
  thrustersPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;
