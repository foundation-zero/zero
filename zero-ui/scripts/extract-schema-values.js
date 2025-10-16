#!/usr/bin/env node

/**
 * Script to extract GraphQL schema types and update definition constants in consts.generated.ts
 * Supports both control and sensor definitions based on type name pattern
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const SCHEMA_PATH = path.join(__dirname, "../src/graphql/thrs/schema.graphql");
const CONSTS_PATH = path.join(__dirname, "../src/lib/consts.generated.ts");

// Parse command line arguments
const args = process.argv.slice(2);
const CONST_NAME = args[0];
const TYPE_NAME = args[1];

// Validate arguments
if (!CONST_NAME || !TYPE_NAME) {
  console.error("❌ Usage: node extract-control-values.js <CONST_NAME> <TYPE_NAME>");
  console.error(
    "   Example: node extract-control-values.js THRUSTERS_CONTROL_DEFINITION ThrustersControlValuesType",
  );
  process.exit(1);
}

// Infer definition type from TYPE_NAME
const isControlDefinition = TYPE_NAME.toLowerCase().includes("control");
const isSensorDefinition = TYPE_NAME.toLowerCase().includes("sensor");
const isParameterDefinition = TYPE_NAME.toLowerCase().includes("parameter");
const isSimulationDefinition = TYPE_NAME.toLowerCase().includes("simulation");

if (
  !isControlDefinition &&
  !isSensorDefinition &&
  !isParameterDefinition &&
  !isSimulationDefinition
) {
  console.error(`❌ Cannot infer definition type from TYPE_NAME: ${TYPE_NAME}`);
  console.error("   TYPE_NAME should contain 'Control', 'Sensor', 'Parameter', or 'Simulation'");
  process.exit(1);
}

/**
 * Parse GraphQL schema to extract ThrustersControlValuesType fields
 */
function inferSensorComponentType(fieldType) {
  const typeMapping = {
    SensorTemperatureSensorType: "Temperature",
    SensorPressureSensorType: "Pressure",
    SensorFlowSensorType: "Flow",
    SensorPumpType: "Pump",
    SensorValveType: "Valve",
    SensorThrusterType: "Thruster",
    SensorPcsType: "Pcs",
  };

  return typeMapping[fieldType] || null;
}

function inferParameterType(fieldName, fieldType) {
  // Infer parameter type from field name patterns
  if (fieldName.toLowerCase().endsWith("temperature")) {
    return "Temperature";
  }
  if (fieldName.toLowerCase().endsWith("flow")) {
    return "Flow";
  }
  if (fieldName.toLowerCase().endsWith("tuning")) {
    return "Tuning";
  }

  // Fallback based on GraphQL type
  if (fieldType === "Float") {
    // Default to Temperature for single Float values
    return "Temperature";
  }
  if (fieldType === "[Float!]") {
    // Array of floats is typically tuning parameters
    return "Tuning";
  }

  return null;
}

function inferSimulationComponentType(fieldName, fieldType) {
  // Map GraphQL types to simulation component types
  const typeMapping = {
    ThrusterSimulationType: "Thruster",
    BoundarySimulationType: "Boundary",
    TemperatureBoundarySimulationType: "Temperature",
    FlowBoundarySimulationType: "Flow",
    PcsSimulationType: "Pcs",
  };

  return typeMapping[fieldType] || null;
}

function parseSchema(schemaPath) {
  try {
    const schema = fs.readFileSync(schemaPath, "utf8");
    const lines = schema.split("\n");

    const extractedValues = {};
    let inTargetType = false;
    let braceCount = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Check if we're entering the target type
      if (line.startsWith(`type ${TYPE_NAME}`)) {
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

      // For parameters, parse fields directly (no @jsonSchemaDirective)
      if (isParameterDefinition) {
        const fieldMatch = line.match(/(\w+):\s*(\[?\w+!?\]?)!/);
        if (!fieldMatch) continue;

        const fieldName = fieldMatch[1];
        const fieldType = fieldMatch[2];

        // Infer parameter type from field name and type
        const parameterType = inferParameterType(fieldName, fieldType);
        if (parameterType) {
          extractedValues[fieldName] = {
            componentType: parameterType,
          };
        }
        continue;
      }

      // For simulation values, parse fields directly (no @jsonSchemaDirective)
      if (isSimulationDefinition) {
        const fieldMatch = line.match(/(\w+):\s*(\w+)!/);
        if (!fieldMatch) continue;

        const fieldName = fieldMatch[1];
        const fieldType = fieldMatch[2];

        // Infer simulation component type from field type
        const simulationComponentType = inferSimulationComponentType(fieldName, fieldType);
        if (simulationComponentType) {
          extractedValues[fieldName] = {
            componentType: simulationComponentType,
          };
        }
        continue;
      }

      // Parse field with @jsonSchemaDirective (for controls and sensors)
      if (line.includes("@jsonSchemaDirective")) {
        const fieldMatch = lines[i - 1]?.match(/(\w+):\s*(\w+)!/);
        if (!fieldMatch) continue;

        const fieldName = fieldMatch[1];
        const fieldType = fieldMatch[2];

        // Extract directive parameters
        const yardTagMatch = line.match(/yardTag:\s*"([^"]+)"/);
        const componentTypeMatch = line.match(/componentType:\s*"([^"]+)"/);
        const valveTypeMatch = line.match(/valveType:\s*"([^"]+)"/);

        if (yardTagMatch) {
          const entry = {
            yardTag: yardTagMatch[1],
            fieldType: fieldType,
          };

          // For control definitions, use componentType from directive
          if (isControlDefinition && componentTypeMatch) {
            entry.componentType = componentTypeMatch[1];
          }

          // For sensor definitions, infer componentType from GraphQL field type
          if (isSensorDefinition) {
            entry.componentType = inferSensorComponentType(fieldType);
          }

          // Add valveType if it exists and is not null
          if (valveTypeMatch) {
            entry.valveType = valveTypeMatch[1];
          }

          extractedValues[fieldName] = entry;
        }
      }
    }

    return extractedValues;
  } catch (error) {
    console.error(`Error parsing schema: ${error.message}`);
    return {};
  }
}

/**
 * Generate TypeScript object string
 */
function generateObjectString(values) {
  const entries = Object.entries(values)
    .map(([key, value]) => {
      const props = [];

      // For parameters and simulation, we don't have yardTag, just componentType
      if (isParameterDefinition) {
        props.push(`componentType: ParametersType.${value.componentType}`);
      } else if (isSimulationDefinition) {
        props.push(`componentType: SimulationComponentType.${value.componentType}`);
      } else {
        // For controls and sensors, include yardTag
        props.push(`yardTag: "${value.yardTag}"`);
      }

      if (isControlDefinition) {
        // For control definitions, include componentType and valveType
        props.push(
          `componentType: ControlComponentType.${value.componentType === "pump" ? "Pump" : "Valve"}`,
        );

        if (value.valveType) {
          // Convert valve type to enum format
          const valveTypeMap = {
            mix: "Mix",
            flowcontrol: "FlowControl",
            shutoff: "Shutoff",
            switch: "Switch",
          };

          const valveTypeEnum = valveTypeMap[value.valveType] || value.valveType;
          props.push(`valveType: ValveType.${valveTypeEnum}`);
        }
      }

      if (isSensorDefinition && value.componentType) {
        // For sensor definitions, include inferred componentType
        props.push(`componentType: SensorComponentType.${value.componentType}`);

        // For sensor valves, also include valveType
        if (value.valveType) {
          const valveTypeMap = {
            mix: "Mix",
            flowcontrol: "FlowControl",
            shutoff: "Shutoff",
            switch: "Switch",
          };

          const valveTypeEnum = valveTypeMap[value.valveType] || value.valveType;
          props.push(`valveType: ValveType.${valveTypeEnum}`);
        }
      }

      return `  ${key}: {\n    ${props.join(",\n    ")},\n  }`;
    })
    .join(",\n");

  const wrapperFunction = isControlDefinition
    ? "toControlDefinition"
    : isSensorDefinition
      ? "toSensorDefinition"
      : isParameterDefinition
        ? "toParameterDefinition"
        : "toSimulationDefinition";
  return `export const ${CONST_NAME} = ${wrapperFunction}({\n${entries},\n});`;
}

/**
 * Update consts.generated.ts file with new object
 */
function updateConstsFile(constsContent, newObjectString) {
  // Pattern to match the existing constant with wrapper function
  const wrapperFunction = isControlDefinition
    ? "toControlDefinition"
    : isSensorDefinition
      ? "toSensorDefinition"
      : isParameterDefinition
        ? "toParameterDefinition"
        : "toSimulationDefinition";

  const pattern = new RegExp(
    `export const ${CONST_NAME} = ${wrapperFunction}\\([\\s\\S]*?\\}\\);`,
    "g",
  );

  if (pattern.test(constsContent)) {
    // Replace existing constant
    return constsContent.replace(pattern, newObjectString);
  } else {
    // Add new constant at the end
    return constsContent + "\n" + newObjectString + "\n";
  }
}

/**
 * Main execution
 */
function main() {
  try {
    const definitionType = isControlDefinition
      ? "control"
      : isSensorDefinition
        ? "sensor"
        : isParameterDefinition
          ? "parameter"
          : "simulation";
    console.log(`🔄 Extracting ${definitionType} values from GraphQL schema...`);
    console.log(`📋 Target: ${CONST_NAME} from ${TYPE_NAME}`);

    // Read schema file
    if (!fs.existsSync(SCHEMA_PATH)) {
      throw new Error(`Schema file not found: ${SCHEMA_PATH}`);
    }

    // Parse schema
    const extractedValues = parseSchema(SCHEMA_PATH);

    if (Object.keys(extractedValues).length === 0) {
      throw new Error(`No fields found in ${TYPE_NAME}`);
    }

    console.log(
      `✓ Found ${Object.keys(extractedValues).length} ${definitionType} values:`,
      Object.keys(extractedValues),
    );

    // Generate new object string
    const newObjectString = generateObjectString(extractedValues);

    // Read and update consts file
    if (!fs.existsSync(CONSTS_PATH)) {
      throw new Error(`Constants file not found: ${CONSTS_PATH}`);
    }

    const constsContent = fs.readFileSync(CONSTS_PATH, "utf8");
    const updatedContent = updateConstsFile(constsContent, newObjectString);

    // Write updated file
    fs.writeFileSync(CONSTS_PATH, updatedContent);

    console.log(`✅ Successfully updated ${CONSTS_PATH}`);
    console.log(`📊 Generated object with ${Object.keys(extractedValues).length} entries`);
  } catch (error) {
    console.error("❌ Error:", error.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { generateObjectString, parseSchema, updateConstsFile };
