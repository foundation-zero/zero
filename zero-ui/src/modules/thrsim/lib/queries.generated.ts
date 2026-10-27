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
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
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
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
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
  }
  thrustersThrusterFwd {
    heatFlow { value timestamp }
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
