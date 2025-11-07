#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const CONSTS_PATH = path.join(__dirname, "../src/lib/consts.generated.ts");
const OUTPUT_PATH = path.join(__dirname, "../src/lib/queries.generated.ts");

// Get command line arguments
const args = process.argv.slice(2);
const INPUT_CONST_NAME = args[0];
const OUTPUT_QUERY_NAME = args[1];

// Validate arguments
if (!INPUT_CONST_NAME || !OUTPUT_QUERY_NAME) {
  console.error("❌ Usage: pnpm generate-graphql-queries <INPUT_CONST_NAME> <OUTPUT_QUERY_NAME>");
  console.error(
    "   Example: pnpm generate-graphql-queries THRUSTERS_CONTROL_DEFINITION THRUSTERS_CONTROL_QUERY",
  );
  console.error(
    "   Example: pnpm generate-graphql-queries THRUSTERS_SENSOR_DEFINITION THRUSTERS_SENSOR_QUERY",
  );
  console.error(
    "   Example: pnpm generate-graphql-queries THRUSTERS_PARAMETER_DEFINITION THRUSTERS_PARAMETER_QUERY",
  );
  console.error(
    "   Example: pnpm generate-graphql-queries THRUSTERS_SIMULATION_INPUTS THRUSTERS_SIMULATION_INPUTS_QUERY",
  );
  process.exit(1);
}

/**
 * Component type field mappings - defines which fields each component type should have
 */
function getComponentTypeFieldMappings() {
  return {
    // Control component type mappings
    ControlComponentType: {
      Pump: ["dutypoint", "on"],
      Valve: ["setpoint"],
      Pcm: ["on"],
    },
    // Sensor component type mappings
    SensorComponentType: {
      Temperature: ["temperature"],
      Pressure: ["pressure"],
      Flow: ["flow", "temperature"],
      Pump: ["flow", "speed", "opTime"],
      Valve: ["positionRel"],
      Thruster: ["active"],
      Pcs: ["mode"],
      Pcm: ["charged"],
    },
    // Simulation component type mappings
    SimulationComponentType: {
      Thruster: ["heatFlow", "active"],
      Boundary: ["temperature", "flow"],
      Temperature: ["temperature"],
      Flow: ["flow"],
      Pcs: ["mode"],
      HeatSource: ["heatFlow"],
    },
    // Parameter component type mappings (parameters are flat, no nested fields)
    ParametersType: {
      Temperature: [],
      Flow: [],
      Tuning: [],
    },
  };
}

/**
 * Extract definitions from the input constant
 */
function getDefinitionsFromConst(constsContent, constName) {
  // Match the constant definition with any wrapper function
  const constMatch = constsContent.match(
    new RegExp(`${constName} = to\\w+Definition\\(\\{([\\s\\S]*?)\\}\\);`),
  );

  if (!constMatch) {
    throw new Error(`Could not find constant: ${constName}`);
  }

  const definitionContent = constMatch[1];
  const definitions = {};

  // Parse field definitions
  const fieldMatches = definitionContent.match(/(\w+):\s*\{([^}]*)\}/g);

  if (!fieldMatches) {
    throw new Error(`No field definitions found in ${constName}`);
  }

  fieldMatches.forEach((fieldMatch) => {
    const [, fieldName, fieldContent] = fieldMatch.match(/(\w+):\s*\{([^}]*)\}/);

    // Parse componentType
    const componentTypeMatch = fieldContent.match(/componentType:\s*(\w+)\.(\w+)/);
    if (!componentTypeMatch) {
      throw new Error(`No componentType found for field: ${fieldName}`);
    }

    const [, componentTypeEnum, componentTypeValue] = componentTypeMatch;

    // Parse optional valveType for valve components
    const valveTypeMatch = fieldContent.match(/valveType:\s*\w+\.(\w+)/);
    const valveType = valveTypeMatch ? valveTypeMatch[1] : null;

    definitions[fieldName] = {
      componentType: componentTypeValue,
      componentTypeEnum,
      valveType,
    };
  });

  return definitions;
}

/**
 * Generate GraphQL query for the given definitions
 */
function generateQuery(definitions) {
  const fieldMappings = getComponentTypeFieldMappings();
  const queryParts = [];

  for (const [fieldName, fieldInfo] of Object.entries(definitions)) {
    const { componentType, componentTypeEnum } = fieldInfo;

    // Get field mappings for this component type
    const componentFields = fieldMappings[componentTypeEnum]?.[componentType] || [];

    if (componentFields.length === 0) {
      // For parameters or components with no nested fields
      if (componentTypeEnum === "ParametersType") {
        queryParts.push(`  ${fieldName}`);
      } else {
        queryParts.push(`  ${fieldName} { value timestamp }`);
      }
    } else {
      // Generate nested field structure
      const fieldLines = componentFields.map((field) => `    ${field} { value timestamp }`);
      queryParts.push([`  ${fieldName} {`, ...fieldLines, "  }"].join("\n"));
    }
  }

  return queryParts.join("\n");
}

/**
 * Update or create queries file
 */
function updateQueriesFile(queryString) {
  let queriesContent = "";

  // Read existing file if it exists
  if (fs.existsSync(OUTPUT_PATH)) {
    queriesContent = fs.readFileSync(OUTPUT_PATH, "utf8");
  }

  const newQueryExport = `export const ${OUTPUT_QUERY_NAME} = \`
${queryString}
\`;`;

  // Create pattern to match existing query
  const pattern = new RegExp(`export const ${OUTPUT_QUERY_NAME} = \`[\\s\\S]*?\`;`, "g");

  if (pattern.test(queriesContent)) {
    // Replace existing query
    queriesContent = queriesContent.replace(pattern, newQueryExport);
  } else {
    // Add new query at the end
    queriesContent += "\n" + newQueryExport + "\n";
  }

  fs.writeFileSync(OUTPUT_PATH, queriesContent);
}

/**
 * Main execution
 */
function main() {
  try {
    console.log(`🔄 Generating GraphQL query...`);
    console.log(`📋 Input: ${INPUT_CONST_NAME}`);
    console.log(`📋 Output: ${OUTPUT_QUERY_NAME}`);

    // Read constants file
    const constsContent = fs.readFileSync(CONSTS_PATH, "utf8");

    // Extract definitions from the input constant
    const definitions = getDefinitionsFromConst(constsContent, INPUT_CONST_NAME);

    const fieldCount = Object.keys(definitions).length;
    if (fieldCount === 0) {
      throw new Error(`No definitions found in ${INPUT_CONST_NAME}`);
    }

    console.log(`✓ Found ${fieldCount} fields:`, Object.keys(definitions));

    // Generate query string
    const queryString = generateQuery(definitions);

    if (!queryString.trim()) {
      throw new Error("Generated query is empty");
    }

    // Update queries file
    updateQueriesFile(queryString);

    console.log(`✅ Successfully updated ${OUTPUT_PATH}`);
    console.log(`📊 Generated query with ${fieldCount} fields`);
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    process.exit(1);
  }
}

// Run the script
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
