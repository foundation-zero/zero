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

echo "📋 Generating THRUSTERS GraphQL queries..."
pnpm run generate-graphql-queries THRUSTERS_CONTROL_DEFINITION THRUSTERS_CONTROL_QUERY
pnpm run generate-graphql-queries THRUSTERS_SENSOR_DEFINITION THRUSTERS_SENSOR_QUERY
pnpm run generate-graphql-queries THRUSTERS_PARAMETER_DEFINITION THRUSTERS_PARAMETERS_QUERY
pnpm run generate-graphql-queries THRUSTERS_SIMULATION_INPUTS THRUSTERS_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries THRUSTERS_SIMULATION_OUTPUTS THRUSTERS_SIMULATION_OUTPUTS_QUERY

# PVT module
echo "📋 Extracting PVT definitions..."
pnpm run extract-schema-values PVT_CONTROL_DEFINITION PvtControlValuesType
pnpm run extract-schema-values PVT_SENSOR_DEFINITION PvtSensorValuesType
pnpm run extract-schema-values PVT_PARAMETER_DEFINITION PvtParametersType
pnpm run extract-schema-values PVT_SIMULATION_INPUTS PvtSimulationInputsType
pnpm run extract-schema-values PVT_SIMULATION_OUTPUTS PvtSimulationOutputsType

echo "📋 Generating PVT GraphQL queries..."
pnpm run generate-graphql-queries PVT_CONTROL_DEFINITION PVT_CONTROL_QUERY
pnpm run generate-graphql-queries PVT_SENSOR_DEFINITION PVT_SENSOR_QUERY
pnpm run generate-graphql-queries PVT_PARAMETER_DEFINITION PVT_PARAMETERS_QUERY
pnpm run generate-graphql-queries PVT_SIMULATION_INPUTS PVT_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries PVT_SIMULATION_OUTPUTS PVT_SIMULATION_OUTPUTS_QUERY

# PCM module
echo "📋 Extracting PCM definitions..."
pnpm run extract-schema-values PCM_CONTROL_DEFINITION PcmControlValuesType
pnpm run extract-schema-values PCM_SENSOR_DEFINITION PcmSensorValuesType
pnpm run extract-schema-values PCM_PARAMETER_DEFINITION PcmParametersType
pnpm run extract-schema-values PCM_SIMULATION_INPUTS PcmSimulationInputsType
pnpm run extract-schema-values PCM_SIMULATION_OUTPUTS PcmSimulationOutputsType

echo "📋 Generating PCM GraphQL queries..."
pnpm run generate-graphql-queries PCM_CONTROL_DEFINITION PCM_CONTROL_QUERY
pnpm run generate-graphql-queries PCM_SENSOR_DEFINITION PCM_SENSOR_QUERY
pnpm run generate-graphql-queries PCM_PARAMETER_DEFINITION PCM_PARAMETERS_QUERY
pnpm run generate-graphql-queries PCM_SIMULATION_INPUTS PCM_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries PCM_SIMULATION_OUTPUTS PCM_SIMULATION_OUTPUTS_QUERY

# CONSUMERS module
echo "📋 Extracting CONSUMERS definitions..."
pnpm run extract-schema-values CONSUMERS_CONTROL_DEFINITION ConsumersControlValuesType
pnpm run extract-schema-values CONSUMERS_SENSOR_DEFINITION ConsumersSensorValuesType
pnpm run extract-schema-values CONSUMERS_PARAMETER_DEFINITION ConsumersParametersType
pnpm run extract-schema-values CONSUMERS_SIMULATION_INPUTS ConsumersSimulationInputsType
pnpm run extract-schema-values CONSUMERS_SIMULATION_OUTPUTS ConsumersSimulationOutputsType

echo "📋 Generating CONSUMERS GraphQL queries..."
pnpm run generate-graphql-queries CONSUMERS_CONTROL_DEFINITION CONSUMERS_CONTROL_QUERY
pnpm run generate-graphql-queries CONSUMERS_SENSOR_DEFINITION CONSUMERS_SENSOR_QUERY
pnpm run generate-graphql-queries CONSUMERS_PARAMETER_DEFINITION CONSUMERS_PARAMETERS_QUERY
pnpm run generate-graphql-queries CONSUMERS_SIMULATION_INPUTS CONSUMERS_SIMULATION_INPUTS_QUERY
pnpm run generate-graphql-queries CONSUMERS_SIMULATION_OUTPUTS CONSUMERS_SIMULATION_OUTPUTS_QUERY

echo "✅ All schema extractions and GraphQL query generations completed!"