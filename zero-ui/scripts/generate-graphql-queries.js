#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const SCHEMA_PATH = path.join(__dirname, "../src/graphql/thrs/schema.graphql");
const CONSTS_PATH = path.join(__dirname, "../src/lib/consts.generated.ts");
const OUTPUT_PATH = path.join(__dirname, "../src/lib/queries.generated.ts");

// Get command line arguments
const args = process.argv.slice(2);
const CONST_NAME = args[0];
const TYPE_NAME = args[1];

// Validate arguments
if (!CONST_NAME || !TYPE_NAME) {
  console.error("❌ Usage: node generate-graphql-queries.js <CONST_NAME> <TYPE_NAME>");
  console.error(
    "   Example: node generate-graphql-queries.js THRUSTERS_CONTROL_QUERY ThrustersControlValuesType",
  );
  process.exit(1);
}

// Infer query type from TYPE_NAME
const isControlQuery = TYPE_NAME.toLowerCase().includes("control");
const isSensorQuery = TYPE_NAME.toLowerCase().includes("sensor");
const isParameterQuery = TYPE_NAME.toLowerCase().includes("parameter");

if (!isControlQuery && !isSensorQuery && !isParameterQuery) {
  console.error(`❌ Cannot infer query type from TYPE_NAME: ${TYPE_NAME}`);
  console.error("   TYPE_NAME should contain 'Control', 'Sensor', or 'Parameter'");
  process.exit(1);
}

/**
 * Get field mappings from CONTROL_FIELDS or SENSOR_FIELDS
 */
function getFieldMappings() {
  try {
    // Read both files to get definitions and field mappings
    const constsGeneratedContent = fs.readFileSync(CONSTS_PATH, "utf8");
    const constsMainContent = fs.readFileSync(path.join(__dirname, "../src/lib/consts.ts"), "utf8");

    let definitionName, fieldMappingName;
    if (isControlQuery) {
      definitionName = "THRUSTERS_CONTROL_DEFINITION";
      fieldMappingName = "CONTROL_FIELDS";
    } else if (isSensorQuery) {
      definitionName = "THRUSTERS_SENSOR_DEFINITION";
      fieldMappingName = "SENSOR_FIELDS";
    } else {
      // For parameters, return all fields since it's a flat structure
      return getParameterFields(constsGeneratedContent);
    }

    // Get component definitions
    const componentDefinitions = getComponentDefinitions(constsGeneratedContent, definitionName);

    // Get field mappings
    const fieldMappings = getFieldMappings_FromConsts(constsMainContent, fieldMappingName);

    return generateFieldsFromMappings(componentDefinitions, fieldMappings);
  } catch (error) {
    console.error(`Error reading field mappings: ${error.message}`);
    return [];
  }
}

function getParameterFields(constsContent) {
  const definitionMatch = constsContent.match(
    /THRUSTERS_PARAMETER_DEFINITION = toParameterDefinition\(\{([\\s\\S]*?)\}\);/,
  );

  if (!definitionMatch) {
    throw new Error("Could not find THRUSTERS_PARAMETER_DEFINITION");
  }

  const definitionContent = definitionMatch[1];
  const fieldMatches = definitionContent.match(/(\w+):\s*\{/g);

  if (!fieldMatches) {
    throw new Error("No fields found in parameter definition");
  }

  return fieldMatches.map((match) => match.replace(/:\s*\{/, ""));
}

function getComponentDefinitions(constsContent, definitionName) {
  const definitionMatch = constsContent.match(
    new RegExp(`${definitionName} = to\\w+Definition\\(\\{([\\s\\S]*?)\\}\\);`),
  );

  if (!definitionMatch) {
    throw new Error(`Could not find ${definitionName}`);
  }

  const definitionContent = definitionMatch[1];
  const componentDefinitions = {};

  // Extract each field with its componentType
  const fieldRegex = /(\w+):\s*\{[^}]*componentType:\s*(\w+)\.(\w+)[^}]*\}/g;
  let match;

  while ((match = fieldRegex.exec(definitionContent)) !== null) {
    const fieldName = match[1];
    const componentType = match[3]; // Get the enum value (Pump, Valve, etc.)
    componentDefinitions[fieldName] = componentType;
  }

  return componentDefinitions;
}

function getFieldMappings_FromConsts(constsContent, fieldMappingName) {
  // Extract the field mapping object
  const mappingRegex = new RegExp(`${fieldMappingName}:[^{]*\\{([\\s\\S]*?)\\};`, "g");
  const mappingMatch = mappingRegex.exec(constsContent);

  if (!mappingMatch) {
    throw new Error(`Could not find ${fieldMappingName}`);
  }

  const mappingContent = mappingMatch[1];
  const fieldMappings = {};

  // Extract each component type mapping
  const componentRegex = /\[(\w+)\.(\w+)\]:\s*\[(.*?)\]/g;
  let match;

  while ((match = componentRegex.exec(mappingContent)) !== null) {
    const componentType = match[2]; // Get the enum value (Pump, Valve, etc.)
    const fieldsStr = match[3];
    const fields = fieldsStr.split(",").map((f) => f.trim().replace(/['"]/g, ""));
    fieldMappings[componentType] = fields;
  }

  return fieldMappings;
}

function generateFieldsFromMappings(componentDefinitions, fieldMappings) {
  const result = {};

  for (const [fieldName, componentType] of Object.entries(componentDefinitions)) {
    const fieldsForComponent = fieldMappings[componentType];
    if (fieldsForComponent) {
      result[fieldName] = {
        componentType: componentType,
        fields: fieldsForComponent,
      };
    }
  }

  return result;
}

/**
 * Parse GraphQL schema to get field type information
 */
function parseSchemaType(typeName) {
  try {
    const schema = fs.readFileSync(SCHEMA_PATH, "utf8");
    const lines = schema.split("\n");

    const typeFields = {};
    let inTargetType = false;
    let braceCount = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Check if we're entering the target type
      if (line.startsWith(`type ${typeName}`)) {
        inTargetType = true;
        braceCount = 0;
        continue;
      }

      if (!inTargetType) continue;

      // Count braces to know when we exit the type
      braceCount += (line.match(/{/g) || []).length;
      braceCount -= (line.match(/}/g) || []).length;

      // If we've closed all braces, we're done with this type
      if (braceCount < 0) {
        break;
      }

      // Parse field definition
      const fieldMatch = line.match(/(\w+):\s*(\w+)!/);
      if (fieldMatch) {
        const fieldName = fieldMatch[1];
        const fieldType = fieldMatch[2];
        typeFields[fieldName] = fieldType;
      }
    }

    return typeFields;
  } catch (error) {
    console.error(`Error parsing schema: ${error.message}`);
    return {};
  }
}

/**
 * Generate GraphQL query string
 */
function generateQuery(fieldMappings, schemaFields) {
  if (isParameterQuery) {
    // For parameters, just list field names (flat structure)
    return fieldMappings.map((field) => `  ${field}`).join("\n");
  }

  // For controls and sensors, use field mappings
  const queryParts = [];

  for (const [fieldName, fieldInfo] of Object.entries(fieldMappings)) {
    const fieldType = schemaFields[fieldName];
    if (!fieldType) {
      console.warn(`⚠️  Field ${fieldName} not found in schema`);
      continue;
    }

    // Generate field block using the specific fields from CONTROL_FIELDS/SENSOR_FIELDS
    const fieldsToInclude = fieldInfo.fields;
    const fieldBlock = [
      `  ${fieldName} {`,
      ...fieldsToInclude.map((field) => `      ${field} { value timestamp }`),
      "      }",
    ];

    queryParts.push(fieldBlock.join("\n"));
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

  const newQueryExport = `export const ${CONST_NAME} = \`\n${queryString}\n\`;\n`;

  // Pattern to match existing query
  const pattern = new RegExp(`export const ${CONST_NAME} = \`[\\s\\S]*?\`;\n?`, "g");

  if (pattern.test(queriesContent)) {
    // Replace existing query
    queriesContent = queriesContent.replace(pattern, newQueryExport);
  } else {
    // Add new query at the end
    queriesContent += "\n" + newQueryExport;
  }

  fs.writeFileSync(OUTPUT_PATH, queriesContent);
}

/**
 * Main execution
 */
function main() {
  try {
    const queryType = isControlQuery ? "control" : isSensorQuery ? "sensor" : "parameter";

    console.log(`🔄 Generating ${queryType} GraphQL query...`);
    console.log(`📋 Target: ${CONST_NAME} from ${TYPE_NAME}`);

    // Get field mappings
    const fieldMappings = getFieldMappings();

    const fieldCount = isParameterQuery ? fieldMappings.length : Object.keys(fieldMappings).length;

    if (fieldCount === 0) {
      throw new Error(`No fields found for ${queryType} definition`);
    }

    console.log(
      `✓ Found ${fieldCount} fields:`,
      isParameterQuery ? fieldMappings : Object.keys(fieldMappings),
    );

    // Parse schema for field types
    const schemaFields = parseSchemaType(TYPE_NAME);

    // Generate query string
    const queryString = generateQuery(fieldMappings, schemaFields);

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
