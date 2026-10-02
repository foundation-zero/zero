export const ADSORPTION_CONTROL_QUERY = `
  adsorptionChiller {
    enable { value timestamp }
  }
  adsorptionFlowcontrolWaste {
    setpoint { value timestamp }
  }
  adsorptionMixHot {
    setpoint { value timestamp }
  }
  adsorptionMixWaste {
    setpoint { value timestamp }
  }
  adsorptionSwitchDhw {
    setpoint { value timestamp }
  }
`;

export const ADSORPTION_CONTROLLER_STATE_QUERY = `

`;

export const ADSORPTION_PARAMETERS_QUERY = `
  adsorptionColdMinimum
  adsorptionColdTrigger
  adsorptionCoolingSetpoint
  adsorptionHotMinimum
  adsorptionHotTrigger
  chillerEnabled
  freeCoolingEnabled
  hotMixTuning
  hotSupplyTemperatureSetpoint
  recoveryTuning
  wasteCoolingTemperatureSetpoint
  wasteCoolingTuning
  wasteRecoveryTemperatureSetpoint
`;

export const ADSORPTION_SENSOR_QUERY = `
  adsorptionAvailableColdTemperature {
    temperature { value timestamp }
  }
  adsorptionAvailableHotTemperature {
    temperature { value timestamp }
  }
  adsorptionAvailableSeawaterTemperature {
    temperature { value timestamp }
  }
  adsorptionChiller {
    operating { value timestamp }
    noError { value timestamp }
    freeCooling { value timestamp }
  }
  adsorptionDhwExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  adsorptionFlowDhw {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  adsorptionFlowHot {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  adsorptionFlowHt {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  adsorptionFlowWaste {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  adsorptionFlowcontrolWaste {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  adsorptionHtExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  adsorptionMixHot {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  adsorptionMixWaste {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  adsorptionSwitchDhw {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  adsorptionTemperatureDhwReturn {
    temperature { value timestamp }
  }
  adsorptionTemperatureHotReturn {
    temperature { value timestamp }
  }
  adsorptionTemperatureHotSupply {
    temperature { value timestamp }
  }
  adsorptionTemperatureHtReturn {
    temperature { value timestamp }
  }
  adsorptionTemperatureHtSupply {
    temperature { value timestamp }
  }
  adsorptionTemperatureWasteReturn {
    temperature { value timestamp }
  }
  adsorptionTemperatureWasteSupply {
    temperature { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const ADSORPTION_SIMULATION_INPUTS_QUERY = `
  adsorptionAvailableColdTemperature {
    temperature { value timestamp }
  }
  adsorptionAvailableHotTemperature {
    temperature { value timestamp }
  }
  adsorptionAvailableSeawaterTemperature {
    temperature { value timestamp }
  }
  adsorptionChiller {
    freeCooling { value timestamp }
  }
  adsorptionConsumersSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  adsorptionCoolingSupply {
    temperature { value timestamp }
  }
  adsorptionDhwSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  adsorptionSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const ADSORPTION_SIMULATION_OUTPUTS_QUERY = `
  adsorptionConsumersReturn {
    temperature { value timestamp }
  }
  adsorptionCoolingReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  adsorptionDhwReturn {
    temperature { value timestamp }
  }
  adsorptionSeawaterReturn {
    temperature { value timestamp }
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

export const CONSUMERS_CONTROLLER_STATE_QUERY = `

`;

export const CONSUMERS_PARAMETERS_QUERY = `
  adsorptionEnabled
  adsorptionFlowBalanceTuning
  adsorptionFlowRatioSetpoint
  bypassFlowBalanceTuning
  dhwEnabled
  dhwFlowBalanceTuning
  dhwFlowRatioSetpoint
`;

export const CONSUMERS_SENSOR_QUERY = `
  consumersAdsorptionExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  consumersDhwExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  consumersFlowAdsorption {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  consumersFlowBypass {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  consumersFlowDhw {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  consumersFlowcontrolAdsorption {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  consumersFlowcontrolBypass {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  consumersFlowcontrolDhw {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  consumersSwitchAdsorption {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  consumersSwitchDhw {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  consumersTemperatureAdsorptionReturn {
    temperature { value timestamp }
  }
  consumersTemperatureAdsorptionSupply {
    temperature { value timestamp }
  }
  consumersTemperatureDhwReturn {
    temperature { value timestamp }
  }
  consumersTemperatureDhwSupply {
    temperature { value timestamp }
  }
  mode {
    mode { value timestamp }
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
  mode {
    mode { value timestamp }
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

export const DC_CONTROL_QUERY = `
  dcMixAft {
    setpoint { value timestamp }
  }
  dcMixExchanger {
    setpoint { value timestamp }
  }
  dcMixFwd {
    setpoint { value timestamp }
  }
  dcMixRecovery {
    setpoint { value timestamp }
  }
  dcMixUgrid {
    setpoint { value timestamp }
  }
  dcPumpAft {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  dcPumpFwd {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  dcPumpUgrid {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  dcSwitchAft1 {
    setpoint { value timestamp }
  }
  dcSwitchAft2 {
    setpoint { value timestamp }
  }
  dcSwitchAft3 {
    setpoint { value timestamp }
  }
  dcSwitchAft4 {
    setpoint { value timestamp }
  }
  dcSwitchFwd1 {
    setpoint { value timestamp }
  }
  dcSwitchFwd2 {
    setpoint { value timestamp }
  }
  dcSwitchUgrid1 {
    setpoint { value timestamp }
  }
  dcSwitchUgrid2 {
    setpoint { value timestamp }
  }
`;

export const DC_CONTROLLER_STATE_QUERY = `

`;

export const DC_PARAMETERS_QUERY = `
  brightloopFlowSetpoint
  brightloopReturnTemperature
  brightloopsAftMixTuning
  brightloopsAftPumpTuning
  brightloopsFwdMixTuning
  brightloopsFwdPumpTuning
  heatDumpTuning
  maximumSupplyTemperature
  recoveryMixTuning
  recoveryTemperature
  ugridFlowSetpoint
  ugridReturnTemperature
  ugridsMixTuning
  ugridsPumpTuning
`;

export const DC_SENSOR_QUERY = `
  dcAftFlow {
    flow { value timestamp }
  }
  dcAftHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dcBrightloopAft1 {
    active { value timestamp }
  }
  dcBrightloopAft2 {
    active { value timestamp }
  }
  dcBrightloopAft3 {
    active { value timestamp }
  }
  dcBrightloopAft4 {
    active { value timestamp }
  }
  dcBrightloopFwd1 {
    active { value timestamp }
  }
  dcBrightloopFwd2 {
    active { value timestamp }
  }
  dcDhwExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dcFlowAft1 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowAft2 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowAft3 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowAft4 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowAftReturn {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowFwd1 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowFwd2 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowFwdReturn {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowUgrid1 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowUgrid2 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFlowUgridReturn {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcFwdFlow {
    flow { value timestamp }
  }
  dcFwdHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dcMixAft {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcMixExchanger {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcMixFwd {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcMixRecovery {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcMixUgrid {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcPressureAft {
    pressure { value timestamp }
  }
  dcPressureFwd {
    pressure { value timestamp }
  }
  dcPressureUgrid {
    pressure { value timestamp }
  }
  dcPumpAft {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcPumpFwd {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcPumpUgrid {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSeawaterExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dcSwitchAft1 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSwitchAft2 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSwitchAft3 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSwitchAft4 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSwitchFwd1 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSwitchFwd2 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSwitchUgrid1 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcSwitchUgrid2 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dcTemperatureAft1Return {
    temperature { value timestamp }
  }
  dcTemperatureAft2Return {
    temperature { value timestamp }
  }
  dcTemperatureAft3Return {
    temperature { value timestamp }
  }
  dcTemperatureAft4Return {
    temperature { value timestamp }
  }
  dcTemperatureAftReturn {
    temperature { value timestamp }
  }
  dcTemperatureAftSupply {
    temperature { value timestamp }
  }
  dcTemperatureFwd1Return {
    temperature { value timestamp }
  }
  dcTemperatureFwd2Return {
    temperature { value timestamp }
  }
  dcTemperatureFwdReturn {
    temperature { value timestamp }
  }
  dcTemperatureFwdSupply {
    temperature { value timestamp }
  }
  dcTemperatureRecovery {
    temperature { value timestamp }
  }
  dcTemperatureRecoveryMix {
    temperature { value timestamp }
  }
  dcTemperatureRecoveryReturn {
    temperature { value timestamp }
  }
  dcTemperatureSupply {
    temperature { value timestamp }
  }
  dcTemperatureUgrid1Return {
    temperature { value timestamp }
  }
  dcTemperatureUgrid2Return {
    temperature { value timestamp }
  }
  dcTemperatureUgridReturn {
    temperature { value timestamp }
  }
  dcTemperatureUgridSupply {
    temperature { value timestamp }
  }
  dcTotalFlow {
    flow { value timestamp }
  }
  dcUgrid1 {
    active { value timestamp }
  }
  dcUgrid2 {
    active { value timestamp }
  }
  dcUgridFlow {
    flow { value timestamp }
  }
  dcUgridHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const DC_SIMULATION_INPUTS_QUERY = `
  dcBrightloopAft1 {
    heatFlow { value timestamp }
  }
  dcBrightloopAft2 {
    heatFlow { value timestamp }
  }
  dcBrightloopAft3 {
    heatFlow { value timestamp }
  }
  dcBrightloopAft4 {
    heatFlow { value timestamp }
  }
  dcBrightloopFwd1 {
    heatFlow { value timestamp }
  }
  dcBrightloopFwd2 {
    heatFlow { value timestamp }
  }
  dcDhwSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dcSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dcUgrid1 {
    heatFlow { value timestamp }
  }
  dcUgrid2 {
    heatFlow { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const DC_SIMULATION_OUTPUTS_QUERY = `
  dcDhwReturn {
    temperature { value timestamp }
  }
  dcSeawaterReturn {
    temperature { value timestamp }
  }
`;

export const DHW_CONTROL_QUERY = `
  dhwFlowcontrolDc {
    setpoint { value timestamp }
  }
  dhwFlowcontrolDrives {
    setpoint { value timestamp }
  }
  dhwHeatpump {
    temperatureSetpoint { value timestamp }
    on { value timestamp }
  }
  dhwPump {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  dhwSwitchHeatpump {
    setpoint { value timestamp }
  }
  dhwSwitchHighTemperature {
    setpoint { value timestamp }
  }
  dhwSwitchLowTemperature {
    setpoint { value timestamp }
  }
  dhwSwitchTank1BoostingReturn {
    setpoint { value timestamp }
  }
  dhwSwitchTank1BoostingSupply {
    setpoint { value timestamp }
  }
  dhwSwitchTank1Inlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank1Outlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank2BoostingReturn {
    setpoint { value timestamp }
  }
  dhwSwitchTank2BoostingSupply {
    setpoint { value timestamp }
  }
  dhwSwitchTank2Inlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank2Outlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank3BoostingReturn {
    setpoint { value timestamp }
  }
  dhwSwitchTank3BoostingSupply {
    setpoint { value timestamp }
  }
  dhwSwitchTank3Inlet {
    setpoint { value timestamp }
  }
  dhwSwitchTank3Outlet {
    setpoint { value timestamp }
  }
`;

export const DHW_CONTROLLER_STATE_QUERY = `
  dhwDcFlowController {
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
  dhwPumpFlowController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  dhwTanksController {
    tank1State { value timestamp }
    tank2State { value timestamp }
    tank3State { value timestamp }
    timeToFill { value timestamp }
    timeToHot { value timestamp }
  }
`;

export const DHW_PARAMETERS_QUERY = `
  boostingMinimumHeat
  boostingStallCooldown
  boostingStallWindow
  boostingStartupGrace
  dcFlowTuning
  dcFlowcontrolMinimumSetpoint
  drivesFlowTuning
  drivesFlowcontrolMinimumSetpoint
  fillingTemperatureSetpoint
  fullLevelLowerBand
  heatpumpBoostingEnabled
  heatpumpFlowSetpoint
  heatpumpTemperatureSetpoint
  htBoostingEnabled
  htBoostingFlowSetpoint
  htBoostingMinimumDelta
  maximumTankLevel
  maximumTankTemperature
  minimumPumpDutypoint
  minimumTankLevel
  minimumTankTemperature
  pumpFlowTuning
  tank1Enabled
  tank2Enabled
  tank3Enabled
`;

export const DHW_SENSOR_QUERY = `
  consumersFlowDhw {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  consumersTemperatureDhwSupply {
    temperature { value timestamp }
  }
  dcFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dcTemperatureRecovery {
    temperature { value timestamp }
  }
  dhwAdsorptionExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwConsumersExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwDcExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwDrivesExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwFlowBoosting {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dhwFlowDc {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dhwFlowDrives {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  dhwFlowcontrolDc {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwFlowcontrolDrives {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwFreshwaterFlowSupply {
    flow { value timestamp }
  }
  dhwHeatpump {
    on { value timestamp }
  }
  dhwHeatpumpHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwHvacExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  dhwLevelSwitchTank1 {
    empty { value timestamp }
  }
  dhwLevelSwitchTank2 {
    empty { value timestamp }
  }
  dhwLevelSwitchTank3 {
    empty { value timestamp }
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
  dhwPressure {
    pressure { value timestamp }
  }
  dhwPump {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchHeatpump {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchHighTemperature {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchLowTemperature {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank1BoostingReturn {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank1BoostingSupply {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank1Inlet {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank1Outlet {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank2BoostingReturn {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank2BoostingSupply {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank2Inlet {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank2Outlet {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank3BoostingReturn {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank3BoostingSupply {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank3Inlet {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  dhwSwitchTank3Outlet {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
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
  dhwTemperatureDcReturn {
    temperature { value timestamp }
  }
  dhwTemperatureDrivesReturn {
    temperature { value timestamp }
  }
  dhwTemperatureFreshwaterSupply {
    temperature { value timestamp }
  }
  dhwTemperatureHvacExchangerReturn {
    temperature { value timestamp }
  }
  dhwTemperatureTank1 {
    temperature { value timestamp }
  }
  dhwTemperatureTank2 {
    temperature { value timestamp }
  }
  dhwTemperatureTank3 {
    temperature { value timestamp }
  }
  drivesFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  drivesTemperatureRecovery {
    temperature { value timestamp }
  }
  freshwaterHotwaterFlow {
    flow { value timestamp }
  }
  freshwaterHotwaterTemperature {
    temperature { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const DHW_SIMULATION_INPUTS_QUERY = `
  dhwAdsorptionSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwConsumersSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwDcSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwDrivesSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwFreshwaterSupply {
    temperature { value timestamp }
    overpressure { value timestamp }
  }
  dhwHotwaterDemand {
    flow { value timestamp }
  }
  dhwHvacExchanger {
    heatFlow { value timestamp }
    maximumTemperature { value timestamp }
  }
  dhwSeawaterSupply {
    temperature { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const DHW_SIMULATION_OUTPUTS_QUERY = `
  dhwAdsorptionReturn {
    temperature { value timestamp }
  }
  dhwConsumersReturn {
    temperature { value timestamp }
  }
  dhwDcReturn {
    temperature { value timestamp }
  }
  dhwDrivesReturn {
    temperature { value timestamp }
  }
  dhwFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwSeawaterReturn {
    temperature { value timestamp }
  }
  dhwSeawaterSupply {
    flow { value timestamp }
  }
`;

export const DRIVES_CONTROL_QUERY = `
  drivesFlowcontrolPropdriveAft {
    setpoint { value timestamp }
  }
  drivesFlowcontrolPropdriveFwd {
    setpoint { value timestamp }
  }
  drivesMixExchanger {
    setpoint { value timestamp }
  }
  drivesMixRecovery {
    setpoint { value timestamp }
  }
  drivesPump1 {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  drivesPump2 {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  drivesSwitchPropdriveAft1 {
    setpoint { value timestamp }
  }
  drivesSwitchPropdriveAft2 {
    setpoint { value timestamp }
  }
  drivesSwitchPropdriveFwd1 {
    setpoint { value timestamp }
  }
  drivesSwitchPropdriveFwd2 {
    setpoint { value timestamp }
  }
  drivesSwitchShorepowerReturn {
    setpoint { value timestamp }
  }
  drivesSwitchShorepowerSupply {
    setpoint { value timestamp }
  }
`;

export const DRIVES_CONTROLLER_STATE_QUERY = `

`;

export const DRIVES_PARAMETERS_QUERY = `
  aftFlowBalanceTuning
  fwdFlowBalanceTuning
  heatDumpTuning
  propulsionDrivesFlowSetpoint
  propulsionMaximumSupplyTemperature
  pumpTuning
  recoveryMixTuning
  recoveryTemperature
  shorepowerFlowSetpoint
  shorepowerMaximumSupplyTemperature
`;

export const DRIVES_SENSOR_QUERY = `
  drivesDhwExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  drivesFlowPropdriveAft1 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  drivesFlowPropdriveAft2 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  drivesFlowPropdriveFwd1 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  drivesFlowPropdriveFwd2 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  drivesFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  drivesFlowShorepower {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  drivesFlowcontrolPropdriveAft {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesFlowcontrolPropdriveFwd {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesMixExchanger {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesMixRecovery {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesPressure {
    pressure { value timestamp }
  }
  drivesPropdriveAft1 {
    active { value timestamp }
  }
  drivesPropdriveAft2 {
    active { value timestamp }
  }
  drivesPropdriveFwd1 {
    active { value timestamp }
  }
  drivesPropdriveFwd2 {
    active { value timestamp }
  }
  drivesPump1 {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesPump2 {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesShorepower {
    active { value timestamp }
  }
  drivesSwitchPropdriveAft1 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesSwitchPropdriveAft2 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesSwitchPropdriveFwd1 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesSwitchPropdriveFwd2 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesSwitchShorepowerReturn {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesSwitchShorepowerSupply {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  drivesTemperaturePropdriveAft1Return {
    temperature { value timestamp }
  }
  drivesTemperaturePropdriveAft2Return {
    temperature { value timestamp }
  }
  drivesTemperaturePropdriveFwd1Return {
    temperature { value timestamp }
  }
  drivesTemperaturePropdriveFwd2Return {
    temperature { value timestamp }
  }
  drivesTemperaturePropdrivesAftSupply {
    temperature { value timestamp }
  }
  drivesTemperaturePropdrivesFwdSupply {
    temperature { value timestamp }
  }
  drivesTemperatureRecovery {
    temperature { value timestamp }
  }
  drivesTemperatureRecoveryMix {
    temperature { value timestamp }
  }
  drivesTemperatureRecoveryReturn {
    temperature { value timestamp }
  }
  drivesTemperatureShorepowerReturn {
    temperature { value timestamp }
  }
  drivesTemperatureSupply {
    temperature { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const DRIVES_SIMULATION_INPUTS_QUERY = `
  drivesDhwSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  drivesOilCoolerAft {
    heatFlow { value timestamp }
  }
  drivesOilCoolerFwd {
    heatFlow { value timestamp }
  }
  drivesPropdriveAft1 {
    heatFlow { value timestamp }
  }
  drivesPropdriveAft2 {
    heatFlow { value timestamp }
  }
  drivesPropdriveFwd1 {
    heatFlow { value timestamp }
  }
  drivesPropdriveFwd2 {
    heatFlow { value timestamp }
  }
  drivesSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  drivesShorepower {
    heatFlow { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
`;

export const DRIVES_SIMULATION_OUTPUTS_QUERY = `
  drivesDhwReturn {
    temperature { value timestamp }
  }
  drivesSeawaterReturn {
    temperature { value timestamp }
  }
`;

export const HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY = `
  consumersAdsorptionSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  consumersDhwSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
  pcmFreshwaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pvtMainAft {
    heatFlow { value timestamp }
  }
  pvtMainFwd {
    heatFlow { value timestamp }
  }
  pvtOwners {
    heatFlow { value timestamp }
  }
  pvtSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
  thrustersSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersThrusterAft {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
    active { value timestamp }
  }
`;

export const HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY = `
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
  pcmFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmPvtReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmThrustersReturn {
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
  thrustersPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersPcmSupply {
    flow { value timestamp }
  }
  thrustersSeawaterReturn {
    temperature { value timestamp }
  }
`;

export const PCM_CONTROL_QUERY = `
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
  pcmModule1 {
    on { value timestamp }
  }
  pcmPump {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pcmSwitchChargingReturn {
    setpoint { value timestamp }
  }
  pcmSwitchChargingSupply {
    setpoint { value timestamp }
  }
  pcmSwitchConsumers {
    setpoint { value timestamp }
  }
  pcmSwitchDischarging {
    setpoint { value timestamp }
  }
`;

export const PCM_CONTROLLER_STATE_QUERY = `
  module1ChargeController {
    charge { value timestamp }
    energy { value timestamp }
    chargingState { value timestamp }
    chargeStatus { value timestamp }
  }
  module2ChargeController {
    charge { value timestamp }
    energy { value timestamp }
    chargingState { value timestamp }
    chargeStatus { value timestamp }
  }
  module3ChargeController {
    charge { value timestamp }
    energy { value timestamp }
    chargingState { value timestamp }
    chargeStatus { value timestamp }
  }
  module4ChargeController {
    charge { value timestamp }
    energy { value timestamp }
    chargingState { value timestamp }
    chargeStatus { value timestamp }
  }
`;

export const PCM_PARAMETERS_QUERY = `
  chargingRequested
  gracePeriod
  minimumChargingTemperature
  module1FlowBalanceTuning
  module2FlowBalanceTuning
  module3FlowBalanceTuning
  module4FlowBalanceTuning
  pcmChargeFlow
  pcmDischargeFlow
  pumpTuning
  retryDelay
  stallDuration
  supplyingRequested
`;

export const PCM_SENSOR_QUERY = `
  consumersFlowAdsorption {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  consumersFlowBypass {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  consumersFlowDhw {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  consumersTemperatureAdsorptionReturn {
    temperature { value timestamp }
  }
  consumersTemperatureDhwReturn {
    temperature { value timestamp }
  }
  freshwaterFlowPcm {
    flow { value timestamp }
  }
  freshwaterTemperaturePcmReturn {
    temperature { value timestamp }
  }
  freshwaterTemperaturePcmSupply {
    temperature { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
  pcmFlowModule1 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pcmFlowModule2 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pcmFlowModule3 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pcmFlowModule4 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pcmFlowcontrolModule1 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmFlowcontrolModule2 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmFlowcontrolModule3 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmFlowcontrolModule4 {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmHeatModule1 {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pcmHeatModule1Freshwater {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pcmHeatModule2 {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pcmHeatModule3 {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pcmHeatModule4 {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pcmPump {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmSwitchChargingReturn {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmSwitchChargingSupply {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmSwitchConsumers {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmSwitchDischarging {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pcmTemperatureConsumersReturn {
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
  pcmTemperatureProducersReturn {
    temperature { value timestamp }
  }
  pcmTemperatureProducersSupply {
    temperature { value timestamp }
  }
`;

export const PCM_SIMULATION_INPUTS_QUERY = `
  mode {
    mode { value timestamp }
  }
  pcmConsumersSupply {
    temperature { value timestamp }
  }
  pcmFreshwaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmPvtSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmThrustersSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const PCM_SIMULATION_OUTPUTS_QUERY = `
  pcmConsumersReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmPvtReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmThrustersReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
`;

export const PVT_CONTROL_QUERY = `
  pvtMixExchanger {
    setpoint { value timestamp }
  }
  pvtMixMainAft {
    setpoint { value timestamp }
  }
  pvtMixMainFwd {
    setpoint { value timestamp }
  }
  pvtMixOwners {
    setpoint { value timestamp }
  }
  pvtPumpMainAft {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pvtPumpMainFwd {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pvtPumpOwners {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  pvtSwitchMainAft {
    setpoint { value timestamp }
  }
  pvtSwitchMainFwd {
    setpoint { value timestamp }
  }
  pvtSwitchOwners {
    setpoint { value timestamp }
  }
`;

export const PVT_CONTROLLER_STATE_QUERY = `
  pvtHeatDumpController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  pvtMainAftPumpController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  pvtMainAftWarmupMixController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  pvtMainFwdPumpController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  pvtMainFwdWarmupMixController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  pvtOwnersPumpController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  pvtOwnersWarmupMixController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
`;

export const PVT_PARAMETERS_QUERY = `
  heatDumpTuning
  mainAftMinimumPumpDutypoint
  mainAftMixTuning
  mainAftPumpTuning
  mainFwdMinimumPumpDutypoint
  mainFwdMixTuning
  mainFwdPumpTuning
  maximumSupplyTemperature
  minimumReturnTemperature
  ownersMinimumPumpDutypoint
  ownersMixTuning
  ownersPumpTuning
  recoveryActivationStringTemperature
  recoveryTemperature
  warmupTemperature
`;

export const PVT_SENSOR_QUERY = `
  mode {
    mode { value timestamp }
  }
  pcmTemperatureProducersSupply {
    temperature { value timestamp }
  }
  pvtFlowMainAftRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainAftStrings {
    flow { value timestamp }
  }
  pvtFlowMainFwdRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainFwdStrings {
    flow { value timestamp }
  }
  pvtFlowMainString10 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString11 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString111 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString112 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString12 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString13 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString21 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString22 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString3 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString4 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString51 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString52 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString61 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString62 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString71 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString72 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString81 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString82 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowMainString9 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersString1 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersString2 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersString3 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersString4 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersString5 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersString6 {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  pvtFlowOwnersStrings {
    flow { value timestamp }
  }
  pvtMaxTemperatureMainAftStrings {
    temperature { value timestamp }
  }
  pvtMaxTemperatureMainFwdStrings {
    temperature { value timestamp }
  }
  pvtMaxTemperatureOwnersStrings {
    temperature { value timestamp }
  }
  pvtMixExchanger {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtMixMainAft {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtMixMainFwd {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtMixOwners {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtPressureMainAft {
    pressure { value timestamp }
  }
  pvtPressureMainFwd {
    pressure { value timestamp }
  }
  pvtPressureMainVacuum {
    pressure { value timestamp }
  }
  pvtPressureOwners {
    pressure { value timestamp }
  }
  pvtPressureOwnersVacuum {
    pressure { value timestamp }
  }
  pvtPressureSystem {
    pressure { value timestamp }
  }
  pvtPumpMainAft {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtPumpMainFwd {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtPumpOwners {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtPvtMainAft {
    power { value timestamp }
  }
  pvtPvtMainAftHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pvtPvtMainFwd {
    power { value timestamp }
  }
  pvtPvtMainFwdHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pvtPvtOwners {
    power { value timestamp }
  }
  pvtPvtOwnersHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pvtPyranometerPs {
    irradiance { value timestamp }
  }
  pvtPyranometerSb {
    irradiance { value timestamp }
  }
  pvtReturnTemperature {
    temperature { value timestamp }
  }
  pvtSeawaterExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  pvtSeawaterExchangerFlow {
    flow { value timestamp }
  }
  pvtSwitchMainAft {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtSwitchMainFwd {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtSwitchOwners {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  pvtTemperatureMainAftReturn {
    temperature { value timestamp }
  }
  pvtTemperatureMainAftStringsReturn {
    temperature { value timestamp }
  }
  pvtTemperatureMainAftStringsSupply {
    temperature { value timestamp }
  }
  pvtTemperatureMainAftSupply {
    temperature { value timestamp }
  }
  pvtTemperatureMainFwdReturn {
    temperature { value timestamp }
  }
  pvtTemperatureMainFwdStringsReturn {
    temperature { value timestamp }
  }
  pvtTemperatureMainFwdStringsSupply {
    temperature { value timestamp }
  }
  pvtTemperatureMainFwdSupply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString10Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString10Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString111Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString112Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString11Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString11Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString12Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString12Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString13Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString13Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString1Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString21Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString22Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString2Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString3Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString3Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString4Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString4Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString51Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString52Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString5Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString61Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString62Return {
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
  pvtTemperatureMainString7Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString81Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString82Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString8Supply {
    temperature { value timestamp }
  }
  pvtTemperatureMainString9Return {
    temperature { value timestamp }
  }
  pvtTemperatureMainString9Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersReturn {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString1Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString1Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString2Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString2Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString3Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString3Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString4Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString4Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString5Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString5Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString6Return {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersString6Supply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersStringsReturn {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersStringsSupply {
    temperature { value timestamp }
  }
  pvtTemperatureOwnersSupply {
    temperature { value timestamp }
  }
  pvtTemperatureSupply {
    temperature { value timestamp }
  }
  pvtTotalFlow {
    flow { value timestamp }
  }
`;

export const PVT_SIMULATION_INPUTS_QUERY = `
  mode {
    mode { value timestamp }
  }
  pvtMainAft {
    heatFlow { value timestamp }
  }
  pvtMainFwd {
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

export const THRS_SIMULATION_INPUTS_QUERY = `
  adsorptionAvailableColdTemperature {
    temperature { value timestamp }
  }
  adsorptionAvailableHotTemperature {
    temperature { value timestamp }
  }
  adsorptionAvailableSeawaterTemperature {
    temperature { value timestamp }
  }
  adsorptionChiller {
    freeCooling { value timestamp }
  }
  adsorptionCoolingSupply {
    temperature { value timestamp }
  }
  adsorptionSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dcBrightloopAft1 {
    heatFlow { value timestamp }
  }
  dcBrightloopAft2 {
    heatFlow { value timestamp }
  }
  dcBrightloopAft3 {
    heatFlow { value timestamp }
  }
  dcBrightloopAft4 {
    heatFlow { value timestamp }
  }
  dcBrightloopFwd1 {
    heatFlow { value timestamp }
  }
  dcBrightloopFwd2 {
    heatFlow { value timestamp }
  }
  dcSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dcUgrid1 {
    heatFlow { value timestamp }
  }
  dcUgrid2 {
    heatFlow { value timestamp }
  }
  dhwFreshwaterSupply {
    temperature { value timestamp }
    overpressure { value timestamp }
  }
  dhwHotwaterDemand {
    flow { value timestamp }
  }
  dhwHvacExchanger {
    heatFlow { value timestamp }
    maximumTemperature { value timestamp }
  }
  dhwSeawaterSupply {
    temperature { value timestamp }
  }
  drivesOilCoolerAft {
    heatFlow { value timestamp }
  }
  drivesOilCoolerFwd {
    heatFlow { value timestamp }
  }
  drivesPropdriveAft1 {
    heatFlow { value timestamp }
  }
  drivesPropdriveAft2 {
    heatFlow { value timestamp }
  }
  drivesPropdriveFwd1 {
    heatFlow { value timestamp }
  }
  drivesPropdriveFwd2 {
    heatFlow { value timestamp }
  }
  drivesSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  drivesShorepower {
    heatFlow { value timestamp }
  }
  mode {
    mode { value timestamp }
  }
  pcmFreshwaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pvtMainAft {
    heatFlow { value timestamp }
  }
  pvtMainFwd {
    heatFlow { value timestamp }
  }
  pvtOwners {
    heatFlow { value timestamp }
  }
  pvtSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
  thrustersSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersThrusterAft {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
    active { value timestamp }
  }
`;

export const THRS_SIMULATION_OUTPUTS_QUERY = `
  adsorptionConsumersReturn {
    temperature { value timestamp }
  }
  adsorptionCoolingReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  adsorptionDhwReturn {
    temperature { value timestamp }
  }
  adsorptionSeawaterReturn {
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
  dcDhwReturn {
    temperature { value timestamp }
  }
  dcSeawaterReturn {
    temperature { value timestamp }
  }
  dhwAdsorptionReturn {
    temperature { value timestamp }
  }
  dhwConsumersReturn {
    temperature { value timestamp }
  }
  dhwDcReturn {
    temperature { value timestamp }
  }
  dhwDrivesReturn {
    temperature { value timestamp }
  }
  dhwFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  dhwSeawaterReturn {
    temperature { value timestamp }
  }
  dhwSeawaterSupply {
    flow { value timestamp }
  }
  drivesDhwReturn {
    temperature { value timestamp }
  }
  drivesSeawaterReturn {
    temperature { value timestamp }
  }
  pcmConsumersReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmFreshwaterReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmPvtReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  pcmThrustersReturn {
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
  thrustersPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersPcmSupply {
    flow { value timestamp }
  }
  thrustersSeawaterReturn {
    temperature { value timestamp }
  }
`;

export const THRUSTERS_CONTROL_QUERY = `
  thrustersFlowcontrolAft {
    setpoint { value timestamp }
  }
  thrustersFlowcontrolFwd {
    setpoint { value timestamp }
  }
  thrustersMixExchanger {
    setpoint { value timestamp }
  }
  thrustersMixRecovery {
    setpoint { value timestamp }
  }
  thrustersPump1 {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  thrustersPump2 {
    dutypoint { value timestamp }
    on { value timestamp }
  }
  thrustersSwitchAft {
    setpoint { value timestamp }
  }
  thrustersSwitchFwd {
    setpoint { value timestamp }
  }
  thrustersSwitchRecovery {
    setpoint { value timestamp }
  }
`;

export const THRUSTERS_CONTROLLER_STATE_QUERY = `
  thrustersAftFlowController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  thrustersAftRecoveryTemperatureController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  thrustersFwdFlowController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  thrustersFwdRecoveryTemperatureController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  thrustersHeatDumpController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  thrustersPumpController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
  thrustersWarmupMixController {
    setpoint { value timestamp }
    measurement { value timestamp }
    output { value timestamp }
    error { value timestamp }
    enabled { value timestamp }
    tuning { value timestamp }
    components { value timestamp }
  }
`;

export const THRUSTERS_PARAMETERS_QUERY = `
  aftFlowBalanceTuning
  aftTemperatureTuning
  coolingFlow
  coolingTemperature
  fwdFlowBalanceTuning
  fwdTemperatureTuning
  heatDumpTuning
  maximumSupplyTemperature
  pumpTuning
  recoveryTemperature
  thrustersMaximumFlow
  thrustersMinimumFlow
  warmupMixTuning
  warmupTemperature
`;

export const THRUSTERS_SENSOR_QUERY = `
  mode {
    mode { value timestamp }
  }
  thrustersFlow {
    flow { value timestamp }
  }
  thrustersFlowAft {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  thrustersFlowFwd {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  thrustersFlowRecovery {
    flow { value timestamp }
    temperature { value timestamp }
    quantity { value timestamp }
  }
  thrustersFlowcontrolAft {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersFlowcontrolFwd {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersMixExchanger {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersMixRecovery {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
  thrustersPressureDischarge {
    pressure { value timestamp }
  }
  thrustersPressureSystem {
    pressure { value timestamp }
  }
  thrustersPump1 {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersPump2 {
    flow { value timestamp }
    speed { value timestamp }
    opTime { value timestamp }
    pressure { value timestamp }
    energyConsumption { value timestamp }
    powerInput { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersSeawaterExchanger {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  thrustersSwitchAft {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersSwitchFwd {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersSwitchRecovery {
    positionRel { value timestamp }
    positionAbs { value timestamp }
    anyFailureActive { value timestamp }
    anyWarningActive { value timestamp }
    feedbackFailure { value timestamp }
    externalOutOfRange { value timestamp }
  }
  thrustersTemperatureAft {
    temperature { value timestamp }
  }
  thrustersTemperatureFwd {
    temperature { value timestamp }
  }
  thrustersTemperaturePreCooler {
    temperature { value timestamp }
  }
  thrustersTemperatureRecovery {
    temperature { value timestamp }
  }
  thrustersTemperatureRecoveryMix {
    temperature { value timestamp }
  }
  thrustersTemperatureSupply {
    temperature { value timestamp }
  }
  thrustersThrusterAft {
    active { value timestamp }
  }
  thrustersThrusterAftHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
  thrustersThrusterFwd {
    active { value timestamp }
  }
  thrustersThrusterFwdHeat {
    temperatureSupply { value timestamp source }
    temperatureReturn { value timestamp source }
    flow { value timestamp source }
    heat { value timestamp }
    deltaT { value timestamp }
  }
`;

export const THRUSTERS_SIMULATION_INPUTS_QUERY = `
  mode {
    mode { value timestamp }
  }
  thrustersPcmSupply {
    temperature { value timestamp }
  }
  thrustersPcs {
    mode { value timestamp }
  }
  thrustersSeawaterSupply {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersThrusterAft {
    heatFlow { value timestamp }
    active { value timestamp }
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
    active { value timestamp }
  }
`;

export const THRUSTERS_SIMULATION_OUTPUTS_QUERY = `
  thrustersPcmReturn {
    temperature { value timestamp }
    flow { value timestamp }
  }
  thrustersPcmSupply {
    flow { value timestamp }
  }
  thrustersSeawaterReturn {
    temperature { value timestamp }
  }
`;
