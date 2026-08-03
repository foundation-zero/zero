#!/usr/bin/env node

/**
 * Script to extract GraphQL schema types and update definition constants in consts.generated.ts
 *
 * This script parses a GraphQL schema file and extracts type definitions to generate
 * TypeScript constants. It supports four definition types:
 * - Control definitions (for control systems)
 * - Sensor definitions (for sensor data)
 * - Parameter definitions (for configuration parameters)
 * - Simulation definitions (for simulation components)
 *
 * Usage:
 *   pnpm tsx scripts/extract-schema-values.ts <CONST_NAME> <TYPE_NAME>
 *
 * Example:
 *   pnpm tsx scripts/extract-schema-values.ts THRUSTERS_CONTROL_DEFINITION ThrustersControlValuesType
 */

import {
  FieldDefinitionNode,
  ObjectTypeDefinitionNode,
  parse,
  TypeNode,
  UnionTypeDefinitionNode,
  visit,
} from "graphql";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// ============================================================================
// Configuration
// ============================================================================

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SCHEMA_PATH = path.join(__dirname, "../src/modules/thrsim/graphql/schema.graphql");
const CONSTS_PATH = path.join(__dirname, "../src/modules/thrsim/lib/consts.generated.ts");

// ============================================================================
// Types
// ============================================================================

type DefinitionType = "control" | "sensor" | "parameter" | "simulation" | "controllerState";

interface DirectiveArgs {
  yardTag?: string;
  componentType?: string;
  valveType?: string;
}

interface ExtractedValue {
  yardTag?: string;
  fieldType?: string;
  componentType?: string;
  valveType?: string;
}

interface ExtractedValues {
  [fieldName: string]: ExtractedValue;
}

interface Config {
  constName: string;
  typeName: string;
  definitionType: DefinitionType;
}

// ============================================================================
// Type Mappings
// ============================================================================

const SENSOR_TYPE_MAP: Record<string, string> = {
  SensorTemperatureSensorType: "Temperature",
  SensorCalculatedTemperatureType: "CalculatedTemperature",
  SensorPressureSensorType: "Pressure",
  SensorFlowSensorType: "Flow",
  SensorPumpType: "Pump",
  SensorValveType: "Valve",
  SensorThrusterType: "Thruster",
  SensorPcsType: "Pcs",
  SensorPcmType: "Pcm",
  SensorLevelSensorType: "Level",
  SensorLevelSwitchType: "LevelSwitch",
  SensorTemperatureDeltaType: "DeltaT",
  SensorCalculatedFlowType: "CalculatedFlow",
  SensorHeatPumpType: "HeatExchanger",
  SensorHeatExchangerType: "HeatExchanger",
  SensorHvacExchangerType: "HeatExchanger",
  SensorPvtType: "HeatExchanger",
  SensorAdsorptionChillerType: "AdsorptionChiller",
  SensorBrightloopType: "Brightloop",
  SensorUgridType: "Ugrid",
  SensorPropulsionDriveType: "PropulsionDrive",
  SensorShorePowerConverterType: "ShorePowerConverter",
};

const SIMULATION_TYPE_MAP: Record<string, string> = {
  SimulationThrusterType: "Thruster",
  SimulationBoundaryType: "Boundary",
  SimulationTemperatureBoundaryType: "Temperature",
  SimulationOverpressureTemperatureBoundaryType: "OverpressureTemperature",
  SimulationFlowBoundaryType: "Flow",
  SimulationPcsType: "Pcs",
  SimulationHeatSourceType: "HeatSource",
  SimulationHvacExchangerType: "HvacExchanger",
};

const CONTROL_TYPE_MAP: Record<string, string> = {
  ControlPcmType: "Pcm",
  ControlPumpType: "Pump",
  ControlValveType: "Valve",
  ControlHeatPumpType: "Heatpump",
  ControlAdsorptionChillerType: "AdsorptionChiller",
};

const CONTROLLER_VALUE_TYPE_MAP: Record<string, string> = {
  ControllerPidControllerValuesType: "PIDController",
  ControllerTanksControllerValuesType: "DhwTanksController",
  ControllerPvtControllerValuesType: "PvtController",
};

const VALVE_TYPE_MAP: Record<string, string> = {
  mix: "Mix",
  flowcontrol: "FlowControl",
  shutoff: "Shutoff",
  switch: "Switch",
  null: "Unknown",
};

// ============================================================================
// Argument Parsing
// ============================================================================

function parseArguments(): Config {
  const args = process.argv.slice(2);
  const [constName, typeName] = args;

  if (!constName || !typeName) {
    console.error("❌ Usage: pnpm tsx scripts/extract-schema-values.ts <CONST_NAME> <TYPE_NAME>");
    console.error(
      "   Example: pnpm tsx scripts/extract-schema-values.ts THRUSTERS_CONTROL_DEFINITION ThrustersControlValuesType",
    );
    process.exit(1);
  }

  const definitionType = inferDefinitionType(typeName);

  return { constName, typeName, definitionType };
}

function inferDefinitionType(typeName: string): DefinitionType {
  const lowerTypeName = typeName.toLowerCase();

  if (lowerTypeName.includes("controlvalues")) return "control";
  if (lowerTypeName.includes("sensorvalues")) return "sensor";
  if (lowerTypeName.includes("parameter")) return "parameter";
  if (lowerTypeName.includes("simulation")) return "simulation";
  if (lowerTypeName.includes("controllerstate")) return "controllerState";

  console.error(`❌ Cannot infer definition type from TYPE_NAME: ${typeName}`);
  console.error(
    "   TYPE_NAME should contain 'Control', 'Sensor', 'Parameter', 'ControllerState' or 'Simulation'",
  );
  return process.exit(1) as never;
}

// ============================================================================
// GraphQL Type Utilities
// ============================================================================

/**
 * Extract the base type name from a GraphQL type, unwrapping NonNull and List modifiers
 */
function getTypeName(type: TypeNode): string {
  if (type.kind === "NonNullType" || type.kind === "ListType") {
    return getTypeName(type.type);
  }
  return type.name.value;
}

// ============================================================================
// Component Type Inference
// ============================================================================

function inferSensorComponentType(fieldType: string): string | null {
  return SENSOR_TYPE_MAP[fieldType] || null;
}

function inferParameterType(fieldName: string, fieldType: string): string | null {
  // Infer from field name patterns
  const lowerFieldName = fieldName.toLowerCase();
  if (lowerFieldName.endsWith("tuning")) return "Tuning";
  if (lowerFieldName.includes("temperature")) return "Temperature";
  if (lowerFieldName.includes("flowcontrol")) return "FlowControl";
  if (lowerFieldName.includes("flow")) return "Flow";
  if (lowerFieldName.includes("enabled")) return "Enabled";
  if (lowerFieldName.includes("ratio")) return "Ratio";
  if (lowerFieldName.includes("coolingsetpoint")) return "Temperature";
  if (lowerFieldName.includes("dutypoint")) return "Dutypoint";
  if (lowerFieldName.includes("hot")) return "Temperature";
  if (lowerFieldName.includes("cold")) return "Temperature";
  if (lowerFieldName.includes("dt") || lowerFieldName.includes("delta")) return "dT";
  if (lowerFieldName.includes("level")) return "Level";
  if (lowerFieldName.includes("disabled")) return "Disabled";

  throw new Error(
    `Cannot infer parameter type from field name: ${fieldName} and type: ${fieldType}`,
  );
}
function inferControlComponentType(fieldType: string): string | null {
  return CONTROL_TYPE_MAP[fieldType] || null;
}

function inferSimulationComponentType(fieldType: string): string | null {
  return SIMULATION_TYPE_MAP[fieldType] || null;
}

function inferControllerComponentType(fieldType: string): string | null {
  return CONTROLLER_VALUE_TYPE_MAP[fieldType] || null;
}
// ============================================================================
// Field Processing
// ============================================================================

function extractDirectiveArgs(field: FieldDefinitionNode): DirectiveArgs {
  const directive = field.directives?.find((d) => d.name.value === "jsonSchemaDirective");
  if (!directive) return {};

  const args: DirectiveArgs = {};
  for (const arg of directive.arguments || []) {
    const argName = arg.name.value as keyof DirectiveArgs;
    if (arg.value.kind === "StringValue") {
      args[argName] = arg.value.value;
    }
  }

  return args;
}

function processParameterField(
  fieldName: string,
  fieldTypeString: string,
  _directiveArgs: DirectiveArgs,
): ExtractedValue | null {
  const parameterType = inferParameterType(fieldName, fieldTypeString);
  if (!parameterType) return null;

  return { componentType: parameterType };
}

function processSimulationField(
  fieldType: string,
  _directiveArgs: DirectiveArgs,
): ExtractedValue | null {
  const simulationComponentType = inferSimulationComponentType(fieldType);
  if (!simulationComponentType) return null;

  return { componentType: simulationComponentType };
}

function processControlField(
  fieldType: string,
  directiveArgs: DirectiveArgs,
): ExtractedValue | null {
  const entry: ExtractedValue = {
    yardTag: directiveArgs.yardTag,
    fieldType: fieldType,
  };

  const componentType = inferControlComponentType(fieldType);
  if (componentType) {
    entry.componentType = componentType;
  }

  if (entry.componentType === "Valve" && directiveArgs.valveType) {
    entry.valveType = directiveArgs.valveType;
  }

  return entry;
}

function processSensorField(
  fieldType: string,
  directiveArgs: DirectiveArgs,
): ExtractedValue | null {
  const entry: ExtractedValue = {
    yardTag: directiveArgs.yardTag,
    fieldType: fieldType,
  };

  const componentType = inferSensorComponentType(fieldType);
  if (componentType) {
    entry.componentType = componentType;
  }

  if (entry.componentType === "Valve" && directiveArgs.valveType) {
    entry.valveType = directiveArgs.valveType;
  }

  return entry;
}

function processControllerField(
  fieldType: string,
  _directiveArgs: DirectiveArgs,
): ExtractedValue | null {
  const entry: ExtractedValue = {
    fieldType: fieldType,
  };

  const componentType = inferControllerComponentType(fieldType);
  if (componentType) {
    entry.componentType = componentType;
  }

  return entry;
}

function processField(
  field: FieldDefinitionNode,
  definitionType: DefinitionType,
): ExtractedValue | null {
  const fieldName = field.name.value;
  const fieldType = getTypeName(field.type);
  const directiveArgs = extractDirectiveArgs(field);

  if (fieldType == "Void") return null;

  switch (definitionType) {
    case "parameter":
      return processParameterField(fieldName, fieldType, directiveArgs);

    case "simulation":
      return processSimulationField(fieldType, directiveArgs);

    case "control":
      return processControlField(fieldType, directiveArgs);

    case "sensor":
      return processSensorField(fieldType, directiveArgs);

    case "controllerState":
      return processControllerField(fieldType, directiveArgs);
  }
}

// ============================================================================
// Schema Parsing
// ============================================================================

function parseSchema(schemaPath: string, config: Config): ExtractedValues {
  try {
    const schemaContent = fs.readFileSync(schemaPath, "utf8");
    const ast = parse(schemaContent);

    const extractedValues: ExtractedValues = {};
    const objectTypes = new Map<string, ObjectTypeDefinitionNode>();
    const unionTypes = new Map<string, UnionTypeDefinitionNode>();

    visit(ast, {
      ObjectTypeDefinition(node: ObjectTypeDefinitionNode) {
        objectTypes.set(node.name.value, node);
      },
      UnionTypeDefinition(node: UnionTypeDefinitionNode) {
        unionTypes.set(node.name.value, node);
      },
    });

    const unionNode = unionTypes.get(config.typeName);
    // If it's a union type, we need to process all member types
    if (unionNode) {
      for (const memberType of unionNode.types || []) {
        const memberNode = objectTypes.get(memberType.name.value);
        if (!memberNode) {
          console.warn(`⚠️  Union member type not found: ${memberType.name.value}`);
          continue;
        }

        for (const field of memberNode.fields || []) {
          const extractedValue = processField(field, config.definitionType);
          if (!extractedValue || extractedValues[field.name.value]) continue;
          extractedValues[field.name.value] = extractedValue;
        }
      }

      return extractedValues;
    }

    const objectNode = objectTypes.get(config.typeName);
    if (!objectNode) {
      console.warn(`⚠️  Type not found in schema: ${config.typeName}`);
      return extractedValues;
    }

    for (const field of objectNode.fields || []) {
      const extractedValue = processField(field, config.definitionType);
      if (extractedValue) {
        extractedValues[field.name.value] = extractedValue;
      }
    }

    return extractedValues;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`Error parsing schema: ${errorMessage}`);
    return {};
  }
}

// ============================================================================
// Code Generation
// ============================================================================

function getWrapperFunction(definitionType: DefinitionType): string {
  const wrapperMap: Record<DefinitionType, string> = {
    control: "toControlDefinition",
    sensor: "toSensorDefinition",
    parameter: "toParameterDefinition",
    simulation: "toSimulationDefinition",
    controllerState: "toControllerStateDefinition",
  };
  return wrapperMap[definitionType];
}

function generatePropertyLines(value: ExtractedValue, definitionType: DefinitionType): string[] {
  const props: string[] = [];

  // Add yardTag: always for control (required), only when present for sensors (optional)
  if (definitionType === "control") {
    props.push(`yardTag: "${value.yardTag ?? ""}"`);
  } else if (definitionType === "sensor" && value.yardTag) {
    props.push(`yardTag: "${value.yardTag}"`);
  }

  // Add componentType based on definition type
  if (definitionType === "parameter" && value.componentType) {
    props.push(`componentType: ParametersType.${value.componentType}`);
  } else if (definitionType === "simulation" && value.componentType) {
    props.push(`componentType: SimulationComponentType.${value.componentType}`);
  } else if (definitionType === "control" && value.componentType) {
    props.push(`componentType: ControlComponentType.${value.componentType}`);
  } else if (definitionType === "sensor" && value.componentType) {
    props.push(`componentType: SensorComponentType.${value.componentType}`);
  } else if (definitionType === "controllerState" && value.componentType) {
    props.push(`componentType: ControllerStateComponentType.${value.componentType}`);
  }

  // Add valveType if applicable
  if (value.valveType) {
    const mappedValveType = VALVE_TYPE_MAP[value.valveType] || value.valveType;
    props.push(`valveType: ValveType.${mappedValveType}`);
  }

  return props;
}

function generateObjectString(values: ExtractedValues, config: Config): string {
  const entries = Object.entries(values)
    .map(([key, value]) => {
      const props = generatePropertyLines(value, config.definitionType);
      return `  ${key}: {\n    ${props.join(",\n    ")},\n  }`;
    })
    .join(",\n");

  const wrapperFunction = getWrapperFunction(config.definitionType);
  const entries_string = entries.length > 0 ? `\n${entries},\n` : "";
  return `export const ${config.constName} = ${wrapperFunction}({${entries_string}});`;
}

function updateConstsFile(constsContent: string, newObjectString: string, config: Config): string {
  // Extract all export const declarations with their wrapper functions
  const constPattern = /export const ([A-Z_]+) = (to\w+Definition)\([\s\S]*?\}\);/g;
  const constants = new Map<string, string>();

  let match;
  while ((match = constPattern.exec(constsContent)) !== null) {
    const [fullMatch, constName] = match;
    if (constName !== config.constName) {
      constants.set(constName, fullMatch);
    }
  }

  // Add or update the target constant
  constants.set(config.constName, newObjectString);

  // Sort constants alphabetically by name
  const sortedEntries = Array.from(constants.entries()).sort(([a], [b]) => a.localeCompare(b));

  // Extract any content before the first export const
  const firstConstMatch = constsContent.match(/export const [A-Z_]+ = to\w+Definition\(/);
  const headerContent = firstConstMatch
    ? constsContent.substring(0, firstConstMatch.index).trimEnd()
    : constsContent;

  // Reconstruct the file with sorted constants
  const sortedConstants = sortedEntries.map(([, constString]) => constString).join("\n\n");

  return headerContent ? `${headerContent}\n\n${sortedConstants}\n` : `${sortedConstants}\n`;
}

// ============================================================================
// File Operations
// ============================================================================

function writeUpdatedConstants(extractedValues: ExtractedValues, config: Config): void {
  console.log(
    `✓ Found ${Object.keys(extractedValues).length} ${config.definitionType} values:`,
    Object.keys(extractedValues),
  );

  const newObjectString = generateObjectString(extractedValues, config);

  if (!fs.existsSync(CONSTS_PATH)) {
    throw new Error(`Constants file not found: ${CONSTS_PATH}`);
  }

  const constsContent = fs.readFileSync(CONSTS_PATH, "utf8");
  const updatedContent = updateConstsFile(constsContent, newObjectString, config);

  fs.writeFileSync(CONSTS_PATH, updatedContent);

  console.log(`✅ Successfully updated ${CONSTS_PATH}`);
  console.log(`📊 Generated object with ${Object.keys(extractedValues).length} entries`);
}

function extractSchemaValues(config: Config): void {
  console.log(`🔄 Extracting ${config.definitionType} values from GraphQL schema...`);
  console.log(`📋 Target: ${config.constName} from ${config.typeName}`);

  if (!fs.existsSync(SCHEMA_PATH)) {
    throw new Error(`Schema file not found: ${SCHEMA_PATH}`);
  }

  const extractedValues = parseSchema(SCHEMA_PATH, config);
  writeUpdatedConstants(extractedValues, config);
}

function runExtractSchemaValues(constName: string, typeName: string): void {
  extractSchemaValues({
    constName,
    typeName,
    definitionType: inferDefinitionType(typeName),
  });
}

// ============================================================================
// Main Execution
// ============================================================================

function main(): void {
  try {
    const config = parseArguments();
    extractSchemaValues(config);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error("❌ Error:", errorMessage);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

// ============================================================================
// Exports (for testing)
// ============================================================================

export {
  extractSchemaValues,
  generateObjectString,
  parseSchema,
  runExtractSchemaValues,
  updateConstsFile,
};
