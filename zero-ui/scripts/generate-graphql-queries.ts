#!/usr/bin/env node

/**
 * Script to generate GraphQL query fragments from TypeScript definition constants
 *
 * This script reads definition constants (control, sensor, parameter, or simulation)
 * and generates corresponding GraphQL query fragments with appropriate field mappings.
 *
 * Usage:
 *   pnpm tsx scripts/generate-graphql-queries.ts <INPUT_CONST_NAME> <OUTPUT_QUERY_NAME>
 *
 * Examples:
 *   pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_CONTROL_DEFINITION THRUSTERS_CONTROL_QUERY
 *   pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_SENSOR_DEFINITION THRUSTERS_SENSOR_QUERY
 *   pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_PARAMETER_DEFINITION THRUSTERS_PARAMETERS_QUERY
 *   pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_SIMULATION_INPUTS THRUSTERS_SIMULATION_INPUTS_QUERY
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// ============================================================================
// Configuration
// ============================================================================

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CONSTS_PATH = path.join(__dirname, "../src/modules/thrsim/lib/consts.generated.ts");
const OUTPUT_PATH = path.join(__dirname, "../src/modules/thrsim/lib/queries.generated.ts");

// ============================================================================
// Types
// ============================================================================

type ComponentTypeEnum =
  | "ControlComponentType"
  | "ControllerStateComponentType"
  | "SensorComponentType"
  | "SimulationComponentType"
  | "ParametersType";

interface FieldDefinition {
  componentType: string;
  componentTypeEnum: ComponentTypeEnum;
  valveType: string | null;
}

interface Definitions {
  [fieldName: string]: FieldDefinition;
}

interface ComponentFieldMappings {
  [componentType: string]: string[];
}

interface AllFieldMappings {
  ControlComponentType: ComponentFieldMappings;
  ControllerStateComponentType: ComponentFieldMappings;
  SensorComponentType: ComponentFieldMappings;
  SimulationComponentType: ComponentFieldMappings;
  ParametersType: ComponentFieldMappings;
}

interface Config {
  inputConstName: string;
  outputQueryName: string;
}

// ============================================================================
// Field Mappings
// ============================================================================

/**
 * Component type field mappings
 * Defines which GraphQL fields each component type should query
 */
const FIELD_MAPPINGS: AllFieldMappings = {
  // Control component fields
  ControlComponentType: {
    Pump: ["dutypoint", "on"],
    Valve: ["setpoint"],
    Pcm: ["on"],
    Heatpump: ["temperatureSetpoint", "on"],
    AdsorptionChiller: ["enable"],
  },

  // Control component fields
  ControllerStateComponentType: {
    Pump: ["dutypoint", "on"],
    Valve: ["setpoint"],
    Pcm: ["on"],
    Heatpump: ["temperatureSetpoint", "on"],
    PIDController: [
      "setpoint",
      "measurement",
      "output",
      "error",
      "enabled",
      "tuning",
      "components",
    ],
    DhwTanksController: ["tank1State", "tank2State", "tank3State", "timeToFill"],
  },

  // Sensor component fields
  SensorComponentType: {
    Temperature: ["temperature"],
    CalculatedTemperature: ["temperature"],
    Pressure: ["pressure"],
    Flow: ["flow", "temperature", "quantity"],
    Pump: [
      "dutypoint",
      "on",
      "flow",
      "speed",
      "opTime",
      "pressure",
      "energyConsumption",
      "powerInput",
    ],
    Valve: ["positionRel", "positionAbs"],
    Thruster: ["active"],
    Pcs: ["mode"],
    Pcm: ["charged"],
    Level: ["level"],
    LevelSwitch: ["empty"],
    DeltaT: ["deltaT"],
    HeatExchanger: ["heat", "deltaT"],
    CalculatedFlow: ["flow"],
    AdsorptionChiller: ["operating", "noError", "freeCooling"],
    Brightloop: ["active"],
    Ugrid: ["active"],
    PropulsionDrive: ["active"],
    ShorePowerConverter: ["active"],
  },

  // Simulation component fields
  SimulationComponentType: {
    Thruster: ["heatFlow", "active"],
    Boundary: ["temperature", "flow"],
    Temperature: ["temperature"],
    OverpressureTemperature: ["temperature", "overpressure"],
    Flow: ["flow"],
    Pcs: ["mode"],
    HeatSource: ["heatFlow"],
    HvacExchanger: ["heatFlow", "maximumTemperature"],
  },

  // Parameter fields (parameters are flat values, no nested fields)
  ParametersType: {
    Temperature: [],
    Flow: [],
    Enabled: [],
    Ratio: [],
    Dutypoint: [],
    dT: [],
    Level: [],
    Disabled: [],
    Tuning: [],
  },
};

// ============================================================================
// Argument Parsing
// ============================================================================

function parseArguments(): Config {
  const args = process.argv.slice(2);
  const [inputConstName, outputQueryName] = args;

  if (!inputConstName || !outputQueryName) {
    console.error(
      "❌ Usage: pnpm tsx scripts/generate-graphql-queries.ts <INPUT_CONST_NAME> <OUTPUT_QUERY_NAME>",
    );
    console.error("   Examples:");
    console.error(
      "     pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_CONTROL_DEFINITION THRUSTERS_CONTROL_QUERY",
    );
    console.error(
      "     pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_SENSOR_DEFINITION THRUSTERS_SENSOR_QUERY",
    );
    console.error(
      "     pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_PARAMETER_DEFINITION THRUSTERS_PARAMETERS_QUERY",
    );
    console.error(
      "     pnpm tsx scripts/generate-graphql-queries.ts THRUSTERS_SIMULATION_INPUTS THRUSTERS_SIMULATION_INPUTS_QUERY",
    );
    return process.exit(1) as never;
  }

  return { inputConstName, outputQueryName };
}

// ============================================================================
// Definition Extraction
// ============================================================================

/**
 * Extract field definitions from a constant in the consts file
 */
function extractDefinitions(constsContent: string, constName: string): Definitions {
  // Match the constant definition with any wrapper function
  const constPattern = new RegExp(`${constName} = to\\w+Definition\\(\\{([\\s\\S]*?)\\}\\);`);
  const constMatch = constsContent.match(constPattern);

  if (!constMatch) {
    throw new Error(`Could not find constant: ${constName}`);
  }

  const definitionContent = constMatch[1];
  const definitions: Definitions = {};

  // Parse field definitions using regex
  const fieldPattern = /(\w+):\s*\{([^}]*)\}/g;
  const fieldMatches = definitionContent.matchAll(fieldPattern);

  for (const fieldMatch of fieldMatches) {
    const fieldName = fieldMatch[1];
    const fieldContent = fieldMatch[2];

    const fieldDef = parseFieldDefinition(fieldName, fieldContent);
    definitions[fieldName] = fieldDef;
  }

  return definitions;
}

/**
 * Parse a single field definition to extract component type information
 */
function parseFieldDefinition(fieldName: string, fieldContent: string): FieldDefinition {
  // Extract componentType (e.g., "ControlComponentType.Pump")
  const componentTypePattern = /componentType:\s*(\w+)\.(\w+)/;
  const componentTypeMatch = fieldContent.match(componentTypePattern);

  if (!componentTypeMatch) {
    throw new Error(`No componentType found for field: ${fieldName}`);
  }

  const componentTypeEnum = componentTypeMatch[1] as ComponentTypeEnum;
  const componentTypeValue = componentTypeMatch[2];

  // Extract optional valveType (e.g., "ValveType.Mix")
  const valveTypePattern = /valveType:\s*\w+\.(\w+)/;
  const valveTypeMatch = fieldContent.match(valveTypePattern);
  const valveType = valveTypeMatch?.[1] ?? null;

  return {
    componentType: componentTypeValue,
    componentTypeEnum,
    valveType,
  };
}

// ============================================================================
// Query Generation
// ============================================================================

/**
 * Generate a GraphQL query fragment for a single field
 */
function generateFieldQuery(fieldName: string, fieldDef: FieldDefinition): string {
  const { componentType, componentTypeEnum } = fieldDef;

  // Get the fields to query for this component type
  const componentFields = FIELD_MAPPINGS[componentTypeEnum]?.[componentType] || [];

  // Parameters are flat values (no nested structure)
  if (componentTypeEnum === "ParametersType") {
    return `  ${fieldName}`;
  }

  // Components with no defined fields get default structure
  if (componentFields.length === 0) {
    return `  ${fieldName} { value timestamp }`;
  }

  // Generate nested field structure
  const nestedFields = componentFields
    .map((field) => `    ${field} { value timestamp }`)
    .join("\n");

  return `  ${fieldName} {\n${nestedFields}\n  }`;
}

/**
 * Generate complete GraphQL query string from definitions
 */
function generateQuery(definitions: Definitions): string {
  const queryParts = Object.entries(definitions).map(([fieldName, fieldDef]) =>
    generateFieldQuery(fieldName, fieldDef),
  );

  return queryParts.join("\n");
}

// ============================================================================
// File Operations
// ============================================================================

/**
 * Update or create the queries file with the generated query
 */
function updateQueriesFile(queryString: string, outputQueryName: string): void {
  let queriesContent = "";

  // Read existing file if it exists
  if (fs.existsSync(OUTPUT_PATH)) {
    queriesContent = fs.readFileSync(OUTPUT_PATH, "utf8");
  }

  // Format the new query export
  const newQueryExport = `export const ${outputQueryName} = \`\n${queryString}\n\`;`;

  // Extract all export const declarations
  const queryPattern = /export const ([A-Z_]+) = `[\s\S]*?`;/g;
  const queries = new Map<string, string>();

  let match;
  while ((match = queryPattern.exec(queriesContent)) !== null) {
    const [fullMatch, queryName] = match;
    if (queryName !== outputQueryName) {
      queries.set(queryName, fullMatch);
    }
  }

  // Add or update the target query
  queries.set(outputQueryName, newQueryExport);

  // Sort queries alphabetically by name
  const sortedEntries = Array.from(queries.entries()).sort(([a], [b]) => a.localeCompare(b));

  // Extract any content before the first export const
  const firstQueryMatch = queriesContent.match(/export const [A-Z_]+ = `/);
  const headerContent = firstQueryMatch
    ? queriesContent.substring(0, firstQueryMatch.index).trimEnd()
    : "";

  // Reconstruct the file with sorted queries
  const sortedQueries = sortedEntries.map(([, queryString]) => queryString).join("\n\n");

  const updatedContent = headerContent
    ? `${headerContent}\n\n${sortedQueries}\n`
    : `${sortedQueries}\n`;

  fs.writeFileSync(OUTPUT_PATH, updatedContent);
}

function generateGraphqlQueries(config: Config): void {
  console.log("🔄 Generating GraphQL query...");
  console.log(`📋 Input: ${config.inputConstName}`);
  console.log(`📋 Output: ${config.outputQueryName}`);

  if (!fs.existsSync(CONSTS_PATH)) {
    throw new Error(`Constants file not found: ${CONSTS_PATH}`);
  }

  const constsContent = fs.readFileSync(CONSTS_PATH, "utf8");
  const definitions = extractDefinitions(constsContent, config.inputConstName);
  const fieldCount = Object.keys(definitions).length;

  console.log(`✓ Found ${fieldCount} fields:`, Object.keys(definitions));

  const queryString = generateQuery(definitions);
  updateQueriesFile(queryString, config.outputQueryName);

  console.log(`✅ Successfully updated ${OUTPUT_PATH}`);
  console.log(`📊 Generated query with ${fieldCount} fields`);
}

function runGenerateGraphqlQueries(inputConstName: string, outputQueryName: string): void {
  generateGraphqlQueries({ inputConstName, outputQueryName });
}

// ============================================================================
// Main Execution
// ============================================================================

function main(): void {
  try {
    const config = parseArguments();
    generateGraphqlQueries(config);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`❌ Error: ${errorMessage}`);
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
  extractDefinitions,
  generateGraphqlQueries,
  generateQuery,
  runGenerateGraphqlQueries,
  updateQueriesFile,
};
