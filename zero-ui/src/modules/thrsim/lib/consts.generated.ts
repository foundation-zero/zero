import { SimulationComponentType, SimulationDefinitions } from "@/modules/thrsim/types";

const toSimulationDefinition = <T extends SimulationDefinitions>(input: T): T => input;

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

export const DC_SIMULATION_INPUTS = toSimulationDefinition({
  dcBrightloopAft1: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopAft2: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopAft3: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopAft4: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopFwd1: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopFwd2: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcDhwSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dcSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dcUgrid1: {
    componentType: SimulationComponentType.Ugrid,
  },
  dcUgrid2: {
    componentType: SimulationComponentType.Ugrid,
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
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesPropdriveAft2: {
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesPropdriveFwd1: {
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesPropdriveFwd2: {
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  drivesShorepower: {
    componentType: SimulationComponentType.ActiveHeatSource,
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
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopAft2: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopAft3: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopAft4: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopFwd1: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcBrightloopFwd2: {
    componentType: SimulationComponentType.ActiveHeatSource,
  },
  dcSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  dcUgrid1: {
    componentType: SimulationComponentType.Ugrid,
  },
  dcUgrid2: {
    componentType: SimulationComponentType.Ugrid,
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
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesPropdriveAft2: {
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesPropdriveFwd1: {
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesPropdriveFwd2: {
    componentType: SimulationComponentType.PropulsionDrive,
  },
  drivesSeawaterSupply: {
    componentType: SimulationComponentType.Boundary,
  },
  drivesShorepower: {
    componentType: SimulationComponentType.ActiveHeatSource,
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
