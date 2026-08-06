#!/usr/bin/env node

import { runExtractSchemaValues } from "./extract-schema-values.ts";
import { runGenerateGraphqlQueries } from "./generate-graphql-queries.ts";

interface ExtractTask {
  constName: string;
  typeName: string;
}

interface QueryTask {
  inputConstName: string;
  outputQueryName: string;
}

interface ModuleTask {
  extractionLabel: string;
  queryLabel: string;
  extractTasks: ExtractTask[];
  queryTasks: QueryTask[];
}

const MODULE_TASKS: ModuleTask[] = [
  {
    extractionLabel: "THRUSTERS definitions",
    queryLabel: "THRUSTERS GraphQL queries",
    extractTasks: [
      { constName: "THRUSTERS_CONTROL_DEFINITION", typeName: "ThrustersControlValuesType" },
      { constName: "THRUSTERS_SENSOR_DEFINITION", typeName: "ThrustersSensorValuesType" },
      { constName: "THRUSTERS_PARAMETER_DEFINITION", typeName: "ThrustersParametersType" },
      { constName: "THRUSTERS_SIMULATION_INPUTS", typeName: "ThrustersSimulationInputsType" },
      { constName: "THRUSTERS_SIMULATION_OUTPUTS", typeName: "ThrustersSimulationOutputsType" },
      { constName: "THRUSTERS_CONTROLLER_STATE", typeName: "ThrustersControllerStateType" },
    ],
    queryTasks: [
      {
        inputConstName: "THRUSTERS_CONTROL_DEFINITION",
        outputQueryName: "THRUSTERS_CONTROL_QUERY",
      },
      { inputConstName: "THRUSTERS_SENSOR_DEFINITION", outputQueryName: "THRUSTERS_SENSOR_QUERY" },
      {
        inputConstName: "THRUSTERS_PARAMETER_DEFINITION",
        outputQueryName: "THRUSTERS_PARAMETERS_QUERY",
      },
      {
        inputConstName: "THRUSTERS_SIMULATION_INPUTS",
        outputQueryName: "THRUSTERS_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "THRUSTERS_SIMULATION_OUTPUTS",
        outputQueryName: "THRUSTERS_SIMULATION_OUTPUTS_QUERY",
      },
      {
        inputConstName: "THRUSTERS_CONTROLLER_STATE",
        outputQueryName: "THRUSTERS_CONTROLLER_STATE_QUERY",
      },
    ],
  },
  {
    extractionLabel: "HIGH TEMPERATURE simulation definitions",
    queryLabel: "HIGH TEMPERATURE GraphQL queries",
    extractTasks: [
      {
        constName: "HIGH_TEMPERATURE_SIMULATION_INPUTS",
        typeName: "HighTemperatureSimulationInputsType",
      },
      {
        constName: "HIGH_TEMPERATURE_SIMULATION_OUTPUTS",
        typeName: "HighTemperatureSimulationOutputsType",
      },
    ],
    queryTasks: [
      {
        inputConstName: "HIGH_TEMPERATURE_SIMULATION_INPUTS",
        outputQueryName: "HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "HIGH_TEMPERATURE_SIMULATION_OUTPUTS",
        outputQueryName: "HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY",
      },
    ],
  },
  {
    extractionLabel: "PVT definitions",
    queryLabel: "PVT GraphQL queries",
    extractTasks: [
      { constName: "PVT_CONTROL_DEFINITION", typeName: "PvtControlValuesType" },
      { constName: "PVT_SENSOR_DEFINITION", typeName: "PvtSensorValuesType" },
      { constName: "PVT_PARAMETER_DEFINITION", typeName: "PvtParametersType" },
      { constName: "PVT_SIMULATION_INPUTS", typeName: "PvtSimulationInputsType" },
      { constName: "PVT_SIMULATION_OUTPUTS", typeName: "PvtSimulationOutputsType" },
      { constName: "PVT_CONTROLLER_STATE", typeName: "PvtControllerStateType" },
    ],
    queryTasks: [
      { inputConstName: "PVT_CONTROL_DEFINITION", outputQueryName: "PVT_CONTROL_QUERY" },
      { inputConstName: "PVT_SENSOR_DEFINITION", outputQueryName: "PVT_SENSOR_QUERY" },
      { inputConstName: "PVT_PARAMETER_DEFINITION", outputQueryName: "PVT_PARAMETERS_QUERY" },
      {
        inputConstName: "PVT_SIMULATION_INPUTS",
        outputQueryName: "PVT_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "PVT_SIMULATION_OUTPUTS",
        outputQueryName: "PVT_SIMULATION_OUTPUTS_QUERY",
      },
      { inputConstName: "PVT_CONTROLLER_STATE", outputQueryName: "PVT_CONTROLLER_STATE_QUERY" },
    ],
  },
  {
    extractionLabel: "PCM definitions",
    queryLabel: "PCM GraphQL queries",
    extractTasks: [
      { constName: "PCM_CONTROL_DEFINITION", typeName: "PcmControlValuesType" },
      { constName: "PCM_SENSOR_DEFINITION", typeName: "PcmSensorValuesType" },
      { constName: "PCM_PARAMETER_DEFINITION", typeName: "PcmParametersType" },
      { constName: "PCM_SIMULATION_INPUTS", typeName: "PcmSimulationInputsType" },
      { constName: "PCM_SIMULATION_OUTPUTS", typeName: "PcmSimulationOutputsType" },
      { constName: "PCM_CONTROLLER_STATE", typeName: "PcmControllerStateType" },
    ],
    queryTasks: [
      { inputConstName: "PCM_CONTROL_DEFINITION", outputQueryName: "PCM_CONTROL_QUERY" },
      { inputConstName: "PCM_SENSOR_DEFINITION", outputQueryName: "PCM_SENSOR_QUERY" },
      { inputConstName: "PCM_PARAMETER_DEFINITION", outputQueryName: "PCM_PARAMETERS_QUERY" },
      {
        inputConstName: "PCM_SIMULATION_INPUTS",
        outputQueryName: "PCM_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "PCM_SIMULATION_OUTPUTS",
        outputQueryName: "PCM_SIMULATION_OUTPUTS_QUERY",
      },
      { inputConstName: "PCM_CONTROLLER_STATE", outputQueryName: "PCM_CONTROLLER_STATE_QUERY" },
    ],
  },
  {
    extractionLabel: "ADSORPTION definitions",
    queryLabel: "ADSORPTION GraphQL queries",
    extractTasks: [
      {
        constName: "ADSORPTION_CONTROL_DEFINITION",
        typeName: "AdsorptionControlValuesType",
      },
      { constName: "ADSORPTION_SENSOR_DEFINITION", typeName: "AdsorptionSensorValuesType" },
      { constName: "ADSORPTION_PARAMETER_DEFINITION", typeName: "AdsorptionParametersType" },
      {
        constName: "ADSORPTION_SIMULATION_INPUTS",
        typeName: "AdsorptionSimulationInputsType",
      },
      {
        constName: "ADSORPTION_SIMULATION_OUTPUTS",
        typeName: "AdsorptionSimulationOutputsType",
      },
      {
        constName: "ADSORPTION_CONTROLLER_STATE",
        typeName: "AdsorptionControllerStateType",
      },
    ],
    queryTasks: [
      {
        inputConstName: "ADSORPTION_CONTROL_DEFINITION",
        outputQueryName: "ADSORPTION_CONTROL_QUERY",
      },
      {
        inputConstName: "ADSORPTION_SENSOR_DEFINITION",
        outputQueryName: "ADSORPTION_SENSOR_QUERY",
      },
      {
        inputConstName: "ADSORPTION_PARAMETER_DEFINITION",
        outputQueryName: "ADSORPTION_PARAMETERS_QUERY",
      },
      {
        inputConstName: "ADSORPTION_SIMULATION_INPUTS",
        outputQueryName: "ADSORPTION_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "ADSORPTION_SIMULATION_OUTPUTS",
        outputQueryName: "ADSORPTION_SIMULATION_OUTPUTS_QUERY",
      },
      {
        inputConstName: "ADSORPTION_CONTROLLER_STATE",
        outputQueryName: "ADSORPTION_CONTROLLER_STATE_QUERY",
      },
    ],
  },
  {
    extractionLabel: "CONSUMERS definitions",
    queryLabel: "CONSUMERS GraphQL queries",
    extractTasks: [
      { constName: "CONSUMERS_CONTROL_DEFINITION", typeName: "ConsumersControlValuesType" },
      { constName: "CONSUMERS_SENSOR_DEFINITION", typeName: "ConsumersSensorValuesType" },
      { constName: "CONSUMERS_PARAMETER_DEFINITION", typeName: "ConsumersParametersType" },
      {
        constName: "CONSUMERS_SIMULATION_INPUTS",
        typeName: "ConsumersSimulationInputsType",
      },
      {
        constName: "CONSUMERS_SIMULATION_OUTPUTS",
        typeName: "ConsumersSimulationOutputsType",
      },
      { constName: "CONSUMERS_CONTROLLER_STATE", typeName: "ConsumersControllerStateType" },
    ],
    queryTasks: [
      {
        inputConstName: "CONSUMERS_CONTROL_DEFINITION",
        outputQueryName: "CONSUMERS_CONTROL_QUERY",
      },
      {
        inputConstName: "CONSUMERS_SENSOR_DEFINITION",
        outputQueryName: "CONSUMERS_SENSOR_QUERY",
      },
      {
        inputConstName: "CONSUMERS_PARAMETER_DEFINITION",
        outputQueryName: "CONSUMERS_PARAMETERS_QUERY",
      },
      {
        inputConstName: "CONSUMERS_SIMULATION_INPUTS",
        outputQueryName: "CONSUMERS_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "CONSUMERS_SIMULATION_OUTPUTS",
        outputQueryName: "CONSUMERS_SIMULATION_OUTPUTS_QUERY",
      },
      {
        inputConstName: "CONSUMERS_CONTROLLER_STATE",
        outputQueryName: "CONSUMERS_CONTROLLER_STATE_QUERY",
      },
    ],
  },
  {
    extractionLabel: "DC definitions",
    queryLabel: "DC GraphQL queries",
    extractTasks: [
      { constName: "DC_CONTROL_DEFINITION", typeName: "DcControlValuesType" },
      { constName: "DC_SENSOR_DEFINITION", typeName: "DcSensorValuesType" },
      { constName: "DC_PARAMETER_DEFINITION", typeName: "DcParametersType" },
      { constName: "DC_SIMULATION_INPUTS", typeName: "DcSimulationInputsType" },
      { constName: "DC_SIMULATION_OUTPUTS", typeName: "DcSimulationOutputsType" },
      { constName: "DC_CONTROLLER_STATE", typeName: "DcControllerStateType" },
    ],
    queryTasks: [
      { inputConstName: "DC_CONTROL_DEFINITION", outputQueryName: "DC_CONTROL_QUERY" },
      { inputConstName: "DC_SENSOR_DEFINITION", outputQueryName: "DC_SENSOR_QUERY" },
      { inputConstName: "DC_PARAMETER_DEFINITION", outputQueryName: "DC_PARAMETERS_QUERY" },
      { inputConstName: "DC_SIMULATION_INPUTS", outputQueryName: "DC_SIMULATION_INPUTS_QUERY" },
      {
        inputConstName: "DC_SIMULATION_OUTPUTS",
        outputQueryName: "DC_SIMULATION_OUTPUTS_QUERY",
      },
      { inputConstName: "DC_CONTROLLER_STATE", outputQueryName: "DC_CONTROLLER_STATE_QUERY" },
    ],
  },
  {
    extractionLabel: "DHW definitions",
    queryLabel: "DHW GraphQL queries",
    extractTasks: [
      { constName: "DHW_CONTROL_DEFINITION", typeName: "DhwControlValuesType" },
      { constName: "DHW_SENSOR_DEFINITION", typeName: "DhwSensorValuesType" },
      { constName: "DHW_PARAMETER_DEFINITION", typeName: "DhwParametersType" },
      { constName: "DHW_SIMULATION_INPUTS", typeName: "DhwSimulationInputsType" },
      { constName: "DHW_SIMULATION_OUTPUTS", typeName: "DhwSimulationOutputsType" },
      { constName: "DHW_CONTROLLER_STATE", typeName: "DhwControllerStateType" },
    ],
    queryTasks: [
      { inputConstName: "DHW_CONTROL_DEFINITION", outputQueryName: "DHW_CONTROL_QUERY" },
      { inputConstName: "DHW_SENSOR_DEFINITION", outputQueryName: "DHW_SENSOR_QUERY" },
      { inputConstName: "DHW_PARAMETER_DEFINITION", outputQueryName: "DHW_PARAMETERS_QUERY" },
      {
        inputConstName: "DHW_SIMULATION_INPUTS",
        outputQueryName: "DHW_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "DHW_SIMULATION_OUTPUTS",
        outputQueryName: "DHW_SIMULATION_OUTPUTS_QUERY",
      },
      { inputConstName: "DHW_CONTROLLER_STATE", outputQueryName: "DHW_CONTROLLER_STATE_QUERY" },
    ],
  },
  {
    extractionLabel: "DRIVES definitions",
    queryLabel: "DRIVES GraphQL queries",
    extractTasks: [
      { constName: "DRIVES_CONTROL_DEFINITION", typeName: "DrivesControlValuesType" },
      { constName: "DRIVES_SENSOR_DEFINITION", typeName: "DrivesSensorValuesType" },
      { constName: "DRIVES_PARAMETER_DEFINITION", typeName: "DrivesParametersType" },
      { constName: "DRIVES_SIMULATION_INPUTS", typeName: "DrivesSimulationInputsType" },
      { constName: "DRIVES_SIMULATION_OUTPUTS", typeName: "DrivesSimulationOutputsType" },
      { constName: "DRIVES_CONTROLLER_STATE", typeName: "DrivesControllerStateType" },
    ],
    queryTasks: [
      {
        inputConstName: "DRIVES_CONTROL_DEFINITION",
        outputQueryName: "DRIVES_CONTROL_QUERY",
      },
      { inputConstName: "DRIVES_SENSOR_DEFINITION", outputQueryName: "DRIVES_SENSOR_QUERY" },
      {
        inputConstName: "DRIVES_PARAMETER_DEFINITION",
        outputQueryName: "DRIVES_PARAMETERS_QUERY",
      },
      {
        inputConstName: "DRIVES_SIMULATION_INPUTS",
        outputQueryName: "DRIVES_SIMULATION_INPUTS_QUERY",
      },
      {
        inputConstName: "DRIVES_SIMULATION_OUTPUTS",
        outputQueryName: "DRIVES_SIMULATION_OUTPUTS_QUERY",
      },
      {
        inputConstName: "DRIVES_CONTROLLER_STATE",
        outputQueryName: "DRIVES_CONTROLLER_STATE_QUERY",
      },
    ],
  },
];

function runModuleTasks(moduleTask: ModuleTask): void {
  console.log(`📋 Extracting ${moduleTask.extractionLabel}...`);
  for (const task of moduleTask.extractTasks) {
    runExtractSchemaValues(task.constName, task.typeName);
  }

  console.log(`📋 Generating ${moduleTask.queryLabel}...`);
  for (const task of moduleTask.queryTasks) {
    runGenerateGraphqlQueries(task.inputConstName, task.outputQueryName);
  }
}

function main(): void {
  try {
    console.log("🚀 Starting extraction of all schema values and generation of GraphQL queries...");
    for (const moduleTask of MODULE_TASKS) {
      runModuleTasks(moduleTask);
    }
    console.log("✅ All schema extractions and GraphQL query generations completed!");
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`❌ Error: ${errorMessage}`);
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
