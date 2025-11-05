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
  thrustersShutoffRecovery {
    setpoint { value timestamp }
  }
  thrustersSwitchAft {
    setpoint { value timestamp }
  }
  thrustersSwitchFwd {
    setpoint { value timestamp }
  }
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
  thrustersTemperatureAftReturn {
    temperature { value timestamp }
  }
  thrustersTemperatureFwdReturn {
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
  thrustersShutoffRecovery {
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
  thrustersPressurePump {
    pressure { value timestamp }
  }
  thrustersPressureRelief {
    pressure { value timestamp }
  }
  thrustersAft {
    active { value timestamp }
  }
  thrustersFwd {
    active { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
`;

export const THRUSTERS_SIMULATION_OUTPUTS_QUERY = `
  thrustersSeawaterReturn {
    temperature { value timestamp }
  }
  thrustersModuleSupply {
    flow { value timestamp }
  }
  thrustersModuleReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const THRUSTERS_SIMULATION_INPUTS_QUERY = `
  thrustersAft {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersFwd {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersModuleSupply {
    temperature { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
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
  pvtModuleSupply {
    temperature { value timestamp }
  }
  pvtSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const PVT_SIMULATION_OUTPUTS_QUERY = `
  pvtModuleReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pvtModuleSupply {
    flow { value timestamp }
  }
  pvtSeawaterReturn {
    temperature { value timestamp }
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
  module1FlowBalanceTuning
  module2FlowBalanceTuning
  module3FlowBalanceTuning
  module4FlowBalanceTuning
`;

export const PCM_SIMULATION_INPUTS_QUERY = `
  pcmProducersSupply {
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
  pcmProducersReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const CONSUMERS_CONTROL_QUERY = `
  consumersSwitchFahrenheitDirectSupply {
    setpoint { value timestamp }
  }
  consumersFlowcontrolFahrenheit {
    setpoint { value timestamp }
  }
  consumersFlowcontrolBypass {
    setpoint { value timestamp }
  }
  consumersFlowcontrolBoosting {
    setpoint { value timestamp }
  }
  consumersSwitchFahrenheitExchanger {
    setpoint { value timestamp }
  }
  consumersSwitchFahrenheitDirectReturn {
    setpoint { value timestamp }
  }
  consumersSwitchBoosting {
    setpoint { value timestamp }
  }
`;

export const CONSUMERS_SENSOR_QUERY = `
  consumersSwitchFahrenheitDirectSupply {
    positionRel { value timestamp }
  }
  consumersTemperatureBoostingReturn {
    temperature { value timestamp }
  }
  consumersTemperatureFahrenheitReturn {
    temperature { value timestamp }
  }
  consumersTemperatureBoostingSupply {
    temperature { value timestamp }
  }
  consumersTemperatureFahrenheitSupply {
    temperature { value timestamp }
  }
  consumersFlowBoosting {
    flow { value timestamp }
    temperature { value timestamp }
  }
  consumersFlowFahrenheit {
    flow { value timestamp }
    temperature { value timestamp }
  }
  consumersFlowBypass {
    flow { value timestamp }
    temperature { value timestamp }
  }
  consumersFlowcontrolFahrenheit {
    positionRel { value timestamp }
  }
  consumersFlowcontrolBypass {
    positionRel { value timestamp }
  }
  consumersFlowcontrolBoosting {
    positionRel { value timestamp }
  }
  consumersSwitchFahrenheitExchanger {
    positionRel { value timestamp }
  }
  consumersSwitchFahrenheitDirectReturn {
    positionRel { value timestamp }
  }
  consumersSwitchBoosting {
    positionRel { value timestamp }
  }
`;

export const CONSUMERS_PARAMETERS_QUERY = `
  boostingFlowRatioSetpoint
  fahrenheitFlowRatioSetpoint
  boostingFlowBalanceTuning
  bypassFlowBalanceTuning
  fahrenheitFlowBalanceTuning
`;

export const CONSUMERS_SIMULATION_INPUTS_QUERY = `
  consumersFahrenheitSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersModuleSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersBoostingSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const CONSUMERS_SIMULATION_OUTPUTS_QUERY = `
  consumersFahrenheitReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersBoostingReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersModuleReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
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
  pcmTemperatureModule1Out {
    temperature { value timestamp }
  }
  pcmTemperatureModule2Out {
    temperature { value timestamp }
  }
  pcmTemperatureModule3Out {
    temperature { value timestamp }
  }
  pcmTemperatureModule4Out {
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
