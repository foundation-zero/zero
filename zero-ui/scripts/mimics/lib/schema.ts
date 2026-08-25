import { FieldDefinitionNode, ObjectTypeDefinitionNode, parse, TypeNode, visit } from "graphql";
import { readFileSync } from "node:fs";
import { SchemaRow } from "./types";

export const MIMIC_MODULES = [
  "thrusters",
  "pcm",
  "pvt",
  "adsorption",
  "consumers",
  "dc",
  "dhw",
  "drives",
] as const;

const SENSOR_SCHEMA_TYPES: Record<string, string> = {
  SensorTemperatureSensorType: "sensor:temperature",
  SensorCalculatedTemperatureType: "sensor:calculatedTemperature",
  SensorPressureSensorType: "sensor:pressure",
  SensorFlowSensorType: "sensor:flow",
  SensorPumpType: "sensor:pump",
  SensorValveType: "sensor:valve",
  SensorThrusterType: "sensor:thruster",
  SensorPcsType: "sensor:pcs",
  SensorPcmType: "sensor:pcm",
  SensorLevelSensorType: "sensor:level",
  SensorLevelSwitchType: "sensor:levelSwitch",
  SensorTemperatureDeltaType: "sensor:deltaT",
  SensorCalculatedFlowType: "sensor:calculatedFlow",
  SensorHeatPumpType: "sensor:heatExchanger",
  SensorHeatExchangerType: "sensor:heatExchanger",
  SensorHvacExchangerType: "sensor:heatExchanger",
  SensorAdsorptionChillerType: "sensor:adsorptionChiller",
  SensorBrightloopType: "sensor:brightloop",
  SensorUgridType: "sensor:ugrid",
  SensorPropulsionDriveType: "sensor:propulsionDrive",
  SensorShorePowerConverterType: "sensor:shorePowerConverter",
};

const CONTROL_SCHEMA_TYPES: Record<string, string> = {
  ControlPcmType: "control:pcm",
  ControlPumpType: "control:pump",
  ControlValveType: "control:valve",
  ControlHeatPumpType: "control:heatpump",
  ControlAdsorptionChillerType: "control:adsorptionChiller",
};

const CONTROLLER_SCHEMA_TYPES: Record<string, string> = {
  ControllerPidControllerValuesType: "pidController",
  ControllerTanksControllerValuesType: "controller:dhwTanksController",
};

export const VALVE_TYPES = new Set(["mix", "flowcontrol", "shutoff", "switch"]);

export const sectionOf = (componentType: string): SchemaRow["section"] => {
  if (componentType.startsWith("sensor:")) return "sensorValues";
  if (componentType.startsWith("control:")) return "controlValues";
  if (componentType.startsWith("parameter:")) return "parameters";
  if (componentType.startsWith("controller:") || componentType === "pidController") {
    return "controllerState";
  }
  throw new Error(`Unknown component type: ${componentType}`);
};

const inferParameterType = (fieldName: string): string => {
  const lower = fieldName.toLowerCase();
  if (lower.endsWith("tuning")) return "parameter:tuning";
  if (lower.includes("temperature")) return "parameter:temperature";
  if (lower.includes("flowcontrol")) return "parameter:flowcontrol";
  if (lower.includes("flow")) return "parameter:flow";
  if (lower.includes("enabled")) return "parameter:enabled";
  if (lower.includes("ratio")) return "parameter:ratio";
  if (lower.includes("coolingsetpoint")) return "parameter:temperature";
  if (lower.includes("dutypoint")) return "parameter:dutypoint";
  if (lower.includes("hot")) return "parameter:temperature";
  if (lower.includes("cold")) return "parameter:temperature";
  if (lower.includes("dt") || lower.includes("delta")) return "parameter:dT";
  if (lower.includes("level")) return "parameter:level";
  if (lower.includes("disabled")) return "parameter:enabled";
  throw new Error(`Cannot infer parameter type from field name: ${fieldName}`);
};

const getTypeName = (type: TypeNode): string => {
  if (type.kind === "NonNullType" || type.kind === "ListType") {
    return getTypeName(type.type);
  }
  return type.name.value;
};

const toUpperCamel = (value: string): string =>
  value
    .split(/[_\s-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

const toKebab = (value: string): string =>
  value
    .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1-$2")
    .toLowerCase();

const friendlyName = (module: string, field: string): string => {
  const stripped = field.startsWith(module) ? field.slice(module.length) : field;
  const camel = stripped.charAt(0).toLowerCase() + stripped.slice(1);
  return toUpperCamel(camel);
};

interface DirectiveArgs {
  yardTag?: string;
  componentType?: string;
  valveType?: string;
}

const extractDirectiveArgs = (field: FieldDefinitionNode): DirectiveArgs => {
  const directive = field.directives?.find((d) => d.name.value === "jsonSchemaDirective");
  if (!directive) return {};
  const args: DirectiveArgs = {};
  for (const arg of directive.arguments ?? []) {
    const name = arg.name.value as keyof DirectiveArgs;
    if (arg.value.kind === "StringValue") {
      args[name] = arg.value.value;
    }
  }
  return args;
};

export const parseSchemaCatalog = (schemaPath: string): SchemaRow[] => {
  const content = readFileSync(schemaPath, "utf8");
  const ast = parse(content);
  const objectTypes = new Map<string, ObjectTypeDefinitionNode>();

  visit(ast, {
    ObjectTypeDefinition(node: ObjectTypeDefinitionNode) {
      objectTypes.set(node.name.value, node);
    },
  });

  const rows: SchemaRow[] = [];

  for (const module of MIMIC_MODULES) {
    const moduleName = module.charAt(0).toUpperCase() + module.slice(1);
    const sections: { key: SchemaRow["section"]; typeName: string }[] = [
      { key: "sensorValues", typeName: `${moduleName}SensorValuesType` },
      { key: "controlValues", typeName: `${moduleName}ControlValuesType` },
      { key: "parameters", typeName: `${moduleName}ParametersType` },
      { key: "controllerState", typeName: `${moduleName}ControllerStateType` },
    ];

    for (const section of sections) {
      const node = objectTypes.get(section.typeName);
      if (!node) {
        console.warn(`⚠️  Type not found in schema: ${section.typeName}`);
        continue;
      }
      for (const field of node.fields ?? []) {
        const fieldName = field.name.value;
        const fieldType = getTypeName(field.type);
        if (fieldType === "Void") continue;

        const args = extractDirectiveArgs(field);
        let componentType: string | null;

        if (section.key === "sensorValues") {
          componentType = SENSOR_SCHEMA_TYPES[fieldType] ?? null;
        } else if (section.key === "controlValues") {
          componentType = CONTROL_SCHEMA_TYPES[fieldType] ?? null;
        } else if (section.key === "parameters") {
          try {
            componentType = inferParameterType(fieldName);
          } catch {
            console.warn(`⚠️  Cannot infer parameter type for ${module}.${fieldName}`);
            continue;
          }
        } else {
          componentType = CONTROLLER_SCHEMA_TYPES[fieldType] ?? null;
        }

        if (!componentType) {
          console.warn(`⚠️  Unmapped schema type ${fieldType} for ${module}.${fieldName}`);
          continue;
        }

        const valveType =
          args.valveType && VALVE_TYPES.has(args.valveType) ? args.valveType : undefined;

        rows.push({
          module,
          section: section.key,
          field: fieldName,
          componentType,
          valveType,
          yardTag: args.yardTag ?? "",
          technicalName: toKebab(fieldName),
          friendlyName: friendlyName(module, fieldName),
        });
      }
    }
  }

  return rows;
};

export const catalogHeaders = [
  "module",
  "section",
  "field",
  "componentType",
  "valveType",
  "yardTag",
  "technicalName",
  "friendlyName",
];

export const toCatalogRow = (row: SchemaRow): Record<string, string> => ({
  module: row.module,
  section: row.section,
  field: row.field,
  componentType: row.componentType,
  valveType: row.valveType ?? "",
  yardTag: row.yardTag,
  technicalName: row.technicalName,
  friendlyName: row.friendlyName,
});
