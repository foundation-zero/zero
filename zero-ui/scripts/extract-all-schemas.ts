#!/usr/bin/env node

import { runExtractSchemaValues } from "./extract-schema-values.ts";
import { runGenerateGraphqlQueries } from "./generate-graphql-queries.ts";

interface Task {
  constName: string;
  typeName: string;
  outputQueryName: string;
}

interface ModuleTask {
  tasks: Task[];
}

type Tasks = {
  [dict_key: string]: ModuleTask;
};

const MODULE_TASKS: Tasks = {
  THRUSTERS: {
    tasks: [
      {
        constName: "THRUSTERS_CONTROL_DEFINITION",
        outputQueryName: "THRUSTERS_CONTROL_QUERY",
        typeName: "ThrustersControlValuesType",
      },
      {
        constName: "THRUSTERS_SENSOR_DEFINITION",
        outputQueryName: "THRUSTERS_SENSOR_QUERY",
        typeName: "ThrustersSensorValuesType",
      },
      {
        constName: "THRUSTERS_PARAMETER_DEFINITION",
        outputQueryName: "THRUSTERS_PARAMETERS_QUERY",
        typeName: "ThrustersParametersType",
      },
      {
        constName: "THRUSTERS_SIMULATION_INPUTS",
        outputQueryName: "THRUSTERS_SIMULATION_INPUTS_QUERY",
        typeName: "ThrustersSimulationInputsType",
      },
      {
        constName: "THRUSTERS_SIMULATION_OUTPUTS",
        outputQueryName: "THRUSTERS_SIMULATION_OUTPUTS_QUERY",
        typeName: "ThrustersSimulationOutputsType",
      },
      {
        constName: "THRUSTERS_CONTROLLER_STATE",
        outputQueryName: "THRUSTERS_CONTROLLER_STATE_QUERY",
        typeName: "ThrustersControllerStateType",
      },
    ],
  },
  "HIGH TEMPERATURE": {
    tasks: [
      {
        constName: "HIGH_TEMPERATURE_SIMULATION_INPUTS",
        outputQueryName: "HIGH_TEMPERATURE_SIMULATION_INPUTS_QUERY",
        typeName: "HighTemperatureSimulationInputsType",
      },
      {
        constName: "HIGH_TEMPERATURE_SIMULATION_OUTPUTS",
        outputQueryName: "HIGH_TEMPERATURE_SIMULATION_OUTPUTS_QUERY",
        typeName: "HighTemperatureSimulationOutputsType",
      },
    ],
  },
  PVT: {
    tasks: [
      {
        constName: "PVT_CONTROL_DEFINITION",
        outputQueryName: "PVT_CONTROL_QUERY",
        typeName: "PvtControlValuesType",
      },
      {
        constName: "PVT_SENSOR_DEFINITION",
        outputQueryName: "PVT_SENSOR_QUERY",
        typeName: "PvtSensorValuesType",
      },
      {
        constName: "PVT_PARAMETER_DEFINITION",
        outputQueryName: "PVT_PARAMETERS_QUERY",
        typeName: "PvtParametersType",
      },
      {
        constName: "PVT_SIMULATION_INPUTS",
        outputQueryName: "PVT_SIMULATION_INPUTS_QUERY",
        typeName: "PvtSimulationInputsType",
      },
      {
        constName: "PVT_SIMULATION_OUTPUTS",
        outputQueryName: "PVT_SIMULATION_OUTPUTS_QUERY",
        typeName: "PvtSimulationOutputsType",
      },
      {
        constName: "PVT_CONTROLLER_STATE",
        outputQueryName: "PVT_CONTROLLER_STATE_QUERY",
        typeName: "PvtControllerStateType",
      },
    ],
  },
  PCM: {
    tasks: [
      {
        constName: "PCM_CONTROL_DEFINITION",
        outputQueryName: "PCM_CONTROL_QUERY",
        typeName: "PcmControlValuesType",
      },
      {
        constName: "PCM_SENSOR_DEFINITION",
        outputQueryName: "PCM_SENSOR_QUERY",
        typeName: "PcmSensorValuesType",
      },
      {
        constName: "PCM_PARAMETER_DEFINITION",
        outputQueryName: "PCM_PARAMETERS_QUERY",
        typeName: "PcmParametersType",
      },
      {
        constName: "PCM_SIMULATION_INPUTS",
        outputQueryName: "PCM_SIMULATION_INPUTS_QUERY",
        typeName: "PcmSimulationInputsType",
      },
      {
        constName: "PCM_SIMULATION_OUTPUTS",
        outputQueryName: "PCM_SIMULATION_OUTPUTS_QUERY",
        typeName: "PcmSimulationOutputsType",
      },
      {
        constName: "PCM_CONTROLLER_STATE",
        outputQueryName: "PCM_CONTROLLER_STATE_QUERY",
        typeName: "PcmControllerStateType",
      },
    ],
  },
  ADSORPTION: {
    tasks: [
      {
        constName: "ADSORPTION_CONTROL_DEFINITION",
        outputQueryName: "ADSORPTION_CONTROL_QUERY",
        typeName: "AdsorptionControlValuesType",
      },
      {
        constName: "ADSORPTION_SENSOR_DEFINITION",
        outputQueryName: "ADSORPTION_SENSOR_QUERY",
        typeName: "AdsorptionSensorValuesType",
      },
      {
        constName: "ADSORPTION_PARAMETER_DEFINITION",
        outputQueryName: "ADSORPTION_PARAMETERS_QUERY",
        typeName: "AdsorptionParametersType",
      },
      {
        constName: "ADSORPTION_SIMULATION_INPUTS",
        outputQueryName: "ADSORPTION_SIMULATION_INPUTS_QUERY",
        typeName: "AdsorptionSimulationInputsType",
      },
      {
        constName: "ADSORPTION_SIMULATION_OUTPUTS",
        outputQueryName: "ADSORPTION_SIMULATION_OUTPUTS_QUERY",
        typeName: "AdsorptionSimulationOutputsType",
      },
      {
        constName: "ADSORPTION_CONTROLLER_STATE",
        outputQueryName: "ADSORPTION_CONTROLLER_STATE_QUERY",
        typeName: "AdsorptionControllerStateType",
      },
    ],
  },
  CONSUMERS: {
    tasks: [
      {
        constName: "CONSUMERS_CONTROL_DEFINITION",
        outputQueryName: "CONSUMERS_CONTROL_QUERY",
        typeName: "ConsumersControlValuesType",
      },
      {
        constName: "CONSUMERS_SENSOR_DEFINITION",
        outputQueryName: "CONSUMERS_SENSOR_QUERY",
        typeName: "ConsumersSensorValuesType",
      },
      {
        constName: "CONSUMERS_PARAMETER_DEFINITION",
        outputQueryName: "CONSUMERS_PARAMETERS_QUERY",
        typeName: "ConsumersParametersType",
      },
      {
        constName: "CONSUMERS_SIMULATION_INPUTS",
        outputQueryName: "CONSUMERS_SIMULATION_INPUTS_QUERY",
        typeName: "ConsumersSimulationInputsType",
      },
      {
        constName: "CONSUMERS_SIMULATION_OUTPUTS",
        outputQueryName: "CONSUMERS_SIMULATION_OUTPUTS_QUERY",
        typeName: "ConsumersSimulationOutputsType",
      },
      {
        constName: "CONSUMERS_CONTROLLER_STATE",
        outputQueryName: "CONSUMERS_CONTROLLER_STATE_QUERY",
        typeName: "ConsumersControllerStateType",
      },
    ],
  },
  DC: {
    tasks: [
      {
        constName: "DC_CONTROL_DEFINITION",
        outputQueryName: "DC_CONTROL_QUERY",
        typeName: "DcControlValuesType",
      },
      {
        constName: "DC_SENSOR_DEFINITION",
        outputQueryName: "DC_SENSOR_QUERY",
        typeName: "DcSensorValuesType",
      },
      {
        constName: "DC_PARAMETER_DEFINITION",
        outputQueryName: "DC_PARAMETERS_QUERY",
        typeName: "DcParametersType",
      },
      {
        constName: "DC_SIMULATION_INPUTS",
        outputQueryName: "DC_SIMULATION_INPUTS_QUERY",
        typeName: "DcSimulationInputsType",
      },
      {
        constName: "DC_SIMULATION_OUTPUTS",
        outputQueryName: "DC_SIMULATION_OUTPUTS_QUERY",
        typeName: "DcSimulationOutputsType",
      },
      {
        constName: "DC_CONTROLLER_STATE",
        outputQueryName: "DC_CONTROLLER_STATE_QUERY",
        typeName: "DcControllerStateType",
      },
    ],
  },
  DHW: {
    tasks: [
      {
        constName: "DHW_CONTROL_DEFINITION",
        outputQueryName: "DHW_CONTROL_QUERY",
        typeName: "DhwControlValuesType",
      },
      {
        constName: "DHW_SENSOR_DEFINITION",
        outputQueryName: "DHW_SENSOR_QUERY",
        typeName: "DhwSensorValuesType",
      },
      {
        constName: "DHW_PARAMETER_DEFINITION",
        outputQueryName: "DHW_PARAMETERS_QUERY",
        typeName: "DhwParametersType",
      },
      {
        constName: "DHW_SIMULATION_INPUTS",
        outputQueryName: "DHW_SIMULATION_INPUTS_QUERY",
        typeName: "DhwSimulationInputsType",
      },
      {
        constName: "DHW_SIMULATION_OUTPUTS",
        outputQueryName: "DHW_SIMULATION_OUTPUTS_QUERY",
        typeName: "DhwSimulationOutputsType",
      },
      {
        constName: "DHW_CONTROLLER_STATE",
        outputQueryName: "DHW_CONTROLLER_STATE_QUERY",
        typeName: "DhwControllerStateType",
      },
    ],
  },
  DRIVES: {
    tasks: [
      {
        constName: "DRIVES_CONTROL_DEFINITION",
        outputQueryName: "DRIVES_CONTROL_QUERY",
        typeName: "DrivesControlValuesType",
      },
      {
        constName: "DRIVES_SENSOR_DEFINITION",
        outputQueryName: "DRIVES_SENSOR_QUERY",
        typeName: "DrivesSensorValuesType",
      },
      {
        constName: "DRIVES_PARAMETER_DEFINITION",
        outputQueryName: "DRIVES_PARAMETERS_QUERY",
        typeName: "DrivesParametersType",
      },
      {
        constName: "DRIVES_SIMULATION_INPUTS",
        outputQueryName: "DRIVES_SIMULATION_INPUTS_QUERY",
        typeName: "DrivesSimulationInputsType",
      },
      {
        constName: "DRIVES_SIMULATION_OUTPUTS",
        outputQueryName: "DRIVES_SIMULATION_OUTPUTS_QUERY",
        typeName: "DrivesSimulationOutputsType",
      },
      {
        constName: "DRIVES_CONTROLLER_STATE",
        outputQueryName: "DRIVES_CONTROLLER_STATE_QUERY",
        typeName: "DrivesControllerStateType",
      },
    ],
  },
};

function runModuleTasks(module: string, moduleTask: ModuleTask): void {
  console.log(`📋 Extracting ${module} definitions ...`);
  for (const task of moduleTask.tasks) {
    runExtractSchemaValues(task.constName, task.typeName);
  }

  console.log(`📋 Generating ${module} GraphQL queries ...`);
  for (const task of moduleTask.tasks) {
    runGenerateGraphqlQueries(task.constName, task.outputQueryName);
  }
}

function main(): void {
  try {
    console.log("🚀 Starting extraction of all schema values and generation of GraphQL queries...");
    for (const module of Object.keys(MODULE_TASKS)) {
      runModuleTasks(module, MODULE_TASKS[module]);
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
