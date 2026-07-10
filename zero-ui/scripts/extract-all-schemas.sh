#!/bin/bash

# Script to extract all schema values and generate GraphQL queries for all modules
# Usage: ./scripts/extract-all-schemas.sh

echo "🚀 Starting extraction of all schema values and generation of GraphQL queries..."

# THRUSTERS module
echo "📋 Extracting THRUSTERS definitions..."
pnpm run extract-schema-values THRUSTERS_CONTROL_DEFINITION ThrustersControlValuesType
pnpm run extract-schema-values THRUSTERS_SENSOR_DEFINITION ThrustersSensorValuesType
pnpm run extract-schema-values THRUSTERS_PARAMETER_DEFINITION ThrustersParametersType
pnpm run extract-schema-values THRUSTERS_SIMULATION_INPUTS ThrustersSimulationInputsType
pnpm run extract-schema-values THRUSTERS_SIMULATION_OUTPUTS ThrustersSimulationOutputsType
pnpm run extract-schema-values THRUSTERS_CONTROLLER_STATE ThrustersControllerStateType

echo "📋 Generating THRUSTERS GraphQL queries..."
pnpm run generate-graphql-queries THRUSTERS_CONTROL_DEFINITION THRUSTERS_CONTROL_QUERY
pnpm run generate-graphql-queries THRUSTERS_SENSOR_DEFINITION THRUSTERS_SENSOR_QUERY
pnpm run generate-graphql-queries THRUSTERS_PARAMETER_DEFINITION THRUSTERS_PARAMETERS_QUERY
pnpm run generate-graphql-queries THRUSTERS_SIMULATION_INPUTS THRUSTERS_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries THRUSTERS_SIMULATION_OUTPUTS THRUSTERS_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries THRUSTERS_CONTROLLER_STATE THRUSTERS_CONTROLLER_STATE_QUERY

# HIGH TEMPERATURE simulation
echo "📋 Extracting HIGH TEMPERATURE simulation definitions..."
pnpm run extract-schema-values HIGH_TEMPERATURE_SIMULATION_INPUTS HighTemperatureSimulationInputsType
pnpm run extract-schema-values HIGH_TEMPERATURE_SIMULATION_OUTPUTS HighTemperatureSimulationOutputsType

echo "📋 Generating HIGH TEMPERATURE GraphQL queries..."
pnpm run generate-graphql-queries HIGH_TEMPERATURE_SIMULATION_INPUTS HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries HIGH_TEMPERATURE_SIMULATION_OUTPUTS HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY

# PVT module
echo "📋 Extracting PVT definitions..."
pnpm run extract-schema-values PVT_CONTROL_DEFINITION PvtControlValuesType
pnpm run extract-schema-values PVT_SENSOR_DEFINITION PvtSensorValuesType
pnpm run extract-schema-values PVT_PARAMETER_DEFINITION PvtParametersType
pnpm run extract-schema-values PVT_SIMULATION_INPUTS PvtSimulationInputsType
pnpm run extract-schema-values PVT_SIMULATION_OUTPUTS PvtSimulationOutputsType
pnpm run extract-schema-values PVT_CONTROLLER_STATE PvtControllerStateType

echo "📋 Generating PVT GraphQL queries..."
pnpm run generate-graphql-queries PVT_CONTROL_DEFINITION PVT_CONTROL_QUERY
pnpm run generate-graphql-queries PVT_SENSOR_DEFINITION PVT_SENSOR_QUERY
pnpm run generate-graphql-queries PVT_PARAMETER_DEFINITION PVT_PARAMETERS_QUERY
pnpm run generate-graphql-queries PVT_SIMULATION_INPUTS PVT_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries PVT_SIMULATION_OUTPUTS PVT_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries PVT_CONTROLLER_STATE PVT_CONTROLLER_STATE_QUERY

# PCM module
echo "📋 Extracting PCM definitions..."
pnpm run extract-schema-values PCM_CONTROL_DEFINITION PcmControlValuesType
pnpm run extract-schema-values PCM_SENSOR_DEFINITION PcmSensorValuesType
pnpm run extract-schema-values PCM_PARAMETER_DEFINITION PcmParametersType
pnpm run extract-schema-values PCM_SIMULATION_INPUTS PcmSimulationInputsType
pnpm run extract-schema-values PCM_SIMULATION_OUTPUTS PcmSimulationOutputsType
pnpm run extract-schema-values PCM_CONTROLLER_STATE PcmControllerStateType

echo "📋 Generating PCM GraphQL queries..."
pnpm run generate-graphql-queries PCM_CONTROL_DEFINITION PCM_CONTROL_QUERY
pnpm run generate-graphql-queries PCM_SENSOR_DEFINITION PCM_SENSOR_QUERY
pnpm run generate-graphql-queries PCM_PARAMETER_DEFINITION PCM_PARAMETERS_QUERY
pnpm run generate-graphql-queries PCM_SIMULATION_INPUTS PCM_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries PCM_SIMULATION_OUTPUTS PCM_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries PCM_CONTROLLER_STATE PCM_CONTROLLER_STATE_QUERY

# ADSORPTION module
echo "📋 Extracting ADSORPTION definitions..."
pnpm run extract-schema-values ADSORPTION_CONTROL_DEFINITION AdsorptionControlValuesType
pnpm run extract-schema-values ADSORPTION_SENSOR_DEFINITION AdsorptionSensorValuesType
pnpm run extract-schema-values ADSORPTION_PARAMETER_DEFINITION AdsorptionParametersType
pnpm run extract-schema-values ADSORPTION_SIMULATION_INPUTS AdsorptionSimulationInputsType
pnpm run extract-schema-values ADSORPTION_SIMULATION_OUTPUTS AdsorptionSimulationOutputsType
pnpm run extract-schema-values ADSORPTION_CONTROLLER_STATE AdsorptionControllerStateType

echo "📋 Generating ADSORPTION GraphQL queries..."
pnpm run generate-graphql-queries ADSORPTION_CONTROL_DEFINITION ADSORPTION_CONTROL_QUERY
pnpm run generate-graphql-queries ADSORPTION_SENSOR_DEFINITION ADSORPTION_SENSOR_QUERY
pnpm run generate-graphql-queries ADSORPTION_PARAMETER_DEFINITION ADSORPTION_PARAMETERS_QUERY
pnpm run generate-graphql-queries ADSORPTION_SIMULATION_INPUTS ADSORPTION_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries ADSORPTION_SIMULATION_OUTPUTS ADSORPTION_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries ADSORPTION_CONTROLLER_STATE ADSORPTION_CONTROLLER_STATE_QUERY

# CONSUMERS module
echo "📋 Extracting CONSUMERS definitions..."
pnpm run extract-schema-values CONSUMERS_CONTROL_DEFINITION ConsumersControlValuesType
pnpm run extract-schema-values CONSUMERS_SENSOR_DEFINITION ConsumersSensorValuesType
pnpm run extract-schema-values CONSUMERS_PARAMETER_DEFINITION ConsumersParametersType
pnpm run extract-schema-values CONSUMERS_SIMULATION_INPUTS ConsumersSimulationInputsType
pnpm run extract-schema-values CONSUMERS_SIMULATION_OUTPUTS ConsumersSimulationOutputsType
pnpm run extract-schema-values CONSUMERS_CONTROLLER_STATE ConsumersControllerStateType

echo "📋 Generating CONSUMERS GraphQL queries..."
pnpm run generate-graphql-queries CONSUMERS_CONTROL_DEFINITION CONSUMERS_CONTROL_QUERY
pnpm run generate-graphql-queries CONSUMERS_SENSOR_DEFINITION CONSUMERS_SENSOR_QUERY
pnpm run generate-graphql-queries CONSUMERS_PARAMETER_DEFINITION CONSUMERS_PARAMETERS_QUERY
pnpm run generate-graphql-queries CONSUMERS_SIMULATION_INPUTS CONSUMERS_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries CONSUMERS_SIMULATION_OUTPUTS CONSUMERS_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries CONSUMERS_CONTROLLER_STATE CONSUMERS_CONTROLLER_STATE_QUERY

# DC module
echo "📋 Extracting DC definitions..."
pnpm run extract-schema-values DC_CONTROL_DEFINITION DcControlValuesType
pnpm run extract-schema-values DC_SENSOR_DEFINITION DcSensorValuesType
pnpm run extract-schema-values DC_PARAMETER_DEFINITION DcParametersType
pnpm run extract-schema-values DC_SIMULATION_INPUTS DcSimulationInputsType
pnpm run extract-schema-values DC_SIMULATION_OUTPUTS DcSimulationOutputsType
pnpm run extract-schema-values DC_CONTROLLER_STATE DcControllerStateType

echo "📋 Generating DC GraphQL queries..."
pnpm run generate-graphql-queries DC_CONTROL_DEFINITION DC_CONTROL_QUERY
pnpm run generate-graphql-queries DC_SENSOR_DEFINITION DC_SENSOR_QUERY
pnpm run generate-graphql-queries DC_PARAMETER_DEFINITION DC_PARAMETERS_QUERY
pnpm run generate-graphql-queries DC_SIMULATION_INPUTS DC_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries DC_SIMULATION_OUTPUTS DC_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries DC_CONTROLLER_STATE DC_CONTROLLER_STATE_QUERY

# DHW module
echo "📋 Extracting DHW definitions..."
pnpm run extract-schema-values DHW_CONTROL_DEFINITION DhwControlValuesType
pnpm run extract-schema-values DHW_SENSOR_DEFINITION DhwSensorValuesType
pnpm run extract-schema-values DHW_PARAMETER_DEFINITION DhwParametersType
pnpm run extract-schema-values DHW_SIMULATION_INPUTS DhwSimulationInputsType
pnpm run extract-schema-values DHW_SIMULATION_OUTPUTS DhwSimulationOutputsType
pnpm run extract-schema-values DHW_CONTROLLER_STATE DhwControllerStateType

echo "📋 Generating DHW GraphQL queries..."
pnpm run generate-graphql-queries DHW_CONTROL_DEFINITION DHW_CONTROL_QUERY
pnpm run generate-graphql-queries DHW_SENSOR_DEFINITION DHW_SENSOR_QUERY
pnpm run generate-graphql-queries DHW_PARAMETER_DEFINITION DHW_PARAMETERS_QUERY
pnpm run generate-graphql-queries DHW_SIMULATION_INPUTS DHW_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries DHW_SIMULATION_OUTPUTS DHW_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries DHW_CONTROLLER_STATE DHW_CONTROLLER_STATE_QUERY

# DRIVES module
echo "📋 Extracting DRIVES definitions..."
pnpm run extract-schema-values DRIVES_CONTROL_DEFINITION DrivesControlValuesType
pnpm run extract-schema-values DRIVES_SENSOR_DEFINITION DrivesSensorValuesType
pnpm run extract-schema-values DRIVES_PARAMETER_DEFINITION DrivesParametersType
pnpm run extract-schema-values DRIVES_SIMULATION_INPUTS DrivesSimulationInputsType
pnpm run extract-schema-values DRIVES_SIMULATION_OUTPUTS DrivesSimulationOutputsType
pnpm run extract-schema-values DRIVES_CONTROLLER_STATE DrivesControllerStateType

echo "📋 Generating DRIVES GraphQL queries..."
pnpm run generate-graphql-queries DRIVES_CONTROL_DEFINITION DRIVES_CONTROL_QUERY
pnpm run generate-graphql-queries DRIVES_SENSOR_DEFINITION DRIVES_SENSOR_QUERY
pnpm run generate-graphql-queries DRIVES_PARAMETER_DEFINITION DRIVES_PARAMETERS_QUERY
pnpm run generate-graphql-queries DRIVES_SIMULATION_INPUTS DRIVES_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries DRIVES_SIMULATION_OUTPUTS DRIVES_SIMULATION_OUTPUTS_QUERY
pnpm run generate-graphql-queries DRIVES_CONTROLLER_STATE DRIVES_CONTROLLER_STATE_QUERY

echo "✅ All schema extractions and GraphQL query generations completed!"