import { mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { FIELD_TYPE_TO_ENUM } from "./enums";
import { SchemaRow } from "./types";

interface FillInRow {
  module: string;
  folder: string;
  instanceKey: string;
  componentType: string;
  title: string;
  tooltipTitle: string;
  tooltipComponentType: string;
  tooltipTechnicalName: string;
  slotId: string;
  kind: string;
  valueKind: string;
  sourceModule: string;
  fieldType: string;
  fieldName: string;
  customTitle: string;
  customYardTag: string;
  customTechnicalName: string;
  literalValue: string;
  refTarget: string;
  pidType: string;
  pidControllerField: string;
  pidSetpointField: string;
  pidOutputMinimumField: string;
}

interface ControllerDef {
  name: string;
  pidType: "temperature" | "flow";
  module: string;
  controllerField: string;
  setpointField?: string;
  outputMinimumField?: string;
}

interface InstanceBuild {
  module: string;
  folder: string;
  key: string;
  componentType: string;
  title: string;
  tooltipTitle: string;
  tooltipComponentType: string;
  tooltipTechnicalName: string;
  rows: FillInRow[];
}

const toFillInRow = (record: Record<string, string>): FillInRow => ({
  module: record.module ?? "",
  folder: record.folder ?? "",
  instanceKey: record.instanceKey ?? "",
  componentType: record.componentType ?? "",
  title: record.title ?? "",
  tooltipTitle: record.tooltipTitle ?? "",
  tooltipComponentType: record.tooltipComponentType ?? "",
  tooltipTechnicalName: record.tooltipTechnicalName ?? "",
  slotId: record.slotId ?? "",
  kind: record.kind ?? "",
  valueKind: record.valueKind ?? "",
  sourceModule: record.sourceModule ?? "",
  fieldType: record.fieldType ?? "",
  fieldName: record.fieldName ?? "",
  customTitle: record.customTitle ?? "",
  customYardTag: record.customYardTag ?? "",
  customTechnicalName: record.customTechnicalName ?? "",
  literalValue: record.literalValue ?? "",
  refTarget: record.refTarget ?? "",
  pidType: record.pidType ?? "",
  pidControllerField: record.pidControllerField ?? "",
  pidSetpointField: record.pidSetpointField ?? "",
  pidOutputMinimumField: record.pidOutputMinimumField ?? "",
});

const hasValue = (row: FillInRow): boolean => {
  switch (row.valueKind) {
    case "field":
      return row.fieldName !== "";
    case "custom":
      return row.customTitle !== "" || row.customYardTag !== "" || row.customTechnicalName !== "";
    case "literal":
      return row.literalValue !== "";
    case "ref":
    case "enum":
      return row.refTarget !== "";
    default:
      return false;
  }
};

const groupBy = <T, K>(items: T[], key: (item: T) => K): Map<K, T[]> => {
  const map = new Map<K, T[]>();
  for (const item of items) {
    const k = key(item);
    const list = map.get(k) ?? [];
    list.push(item);
    map.set(k, list);
  }
  return map;
};

const moduleUpper = (module: string): string => module.toUpperCase();

const FOLDER_SUFFIX: Record<string, string> = {
  "boiler-tanks": "TANK_DATA",
  "connecting-circuits": "FRESHWATER_CIRCUIT_DATA",
  "exchange-circuits": "EXCHANGE_CIRCUIT_DATA",
  assets: "ASSET_DATA",
  "level-switches": "LEVEL_SWITCHES_DATA",
  "level-sensors": "LEVEL_SENSOR_DATA",
  "flow-control-valves": "FLOW_CONTROL_VALVE_DATA",
  "flow-sensors": "FLOW_SENSOR_DATA",
  "manual-valves": "MANUAL_VALVE_DATA",
  "pressure-sensors": "PRESSURE_SENSOR_DATA",
  "temperature-sensors": "TEMPERATURE_SENSOR_DATA",
  pumps: "PUMP_DATA",
  "mix-valves": "MIX_VALVE_DATA",
  "switch-valves": "SWITCH_VALVE_DATA",
  "check-valves": "CHECK_VALVE_DATA",
  "heat-exchangers": "HEAT_EXCHANGER_DATA",
};

const singularize = (word: string): string => (word.endsWith("s") ? word.slice(0, -1) : word);

const folderConst = (module: string, folder: string): string => {
  const suffix =
    FOLDER_SUFFIX[folder] ?? `${singularize(folder).toUpperCase().replace(/-/g, "_")}_DATA`;
  return `${moduleUpper(module)}_${suffix}`;
};

const fileBase = (key: string): string => `_${key.replace(/-/g, "_")}`;

const escapeString = (value: string): string =>
  value.replaceAll("\\", "\\\\").replaceAll('"', '\\"');

const sectionOfSlot = (slotId: string): string => slotId.split(".")[0] ?? "";

const slotKey = (slotId: string): string => {
  const dot = slotId.indexOf(".");
  return dot === -1 ? "" : slotId.slice(dot + 1);
};

const PARAM_MEMBER_TO_FIELD_TYPE: Record<string, string> = {
  Temperature: "parameter:temperature",
  Flow: "parameter:flow",
  FlowControl: "parameter:flowcontrol",
  Tuning: "parameter:tuning",
  Enabled: "parameter:enabled",
  Ratio: "parameter:ratio",
  Dutypoint: "parameter:dutypoint",
  dT: "parameter:dT",
  Level: "parameter:level",
};

const paramMemberOf = (fieldType: string): string =>
  Object.entries(PARAM_MEMBER_TO_FIELD_TYPE).find(([, v]) => v === fieldType)?.[0] ?? "Temperature";

const inferParameterFieldType = (fieldName: string): string => {
  const lower = fieldName.toLowerCase();
  if (lower.endsWith("tuning")) return "parameter:tuning";
  if (lower.includes("temperature")) return "parameter:temperature";
  if (lower.includes("flowcontrol")) return "parameter:flowcontrol";
  if (lower.includes("flow")) return "parameter:flow";
  if (lower.includes("enabled")) return "parameter:enabled";
  if (lower.includes("ratio")) return "parameter:ratio";
  if (lower.includes("dutypoint")) return "parameter:dutypoint";
  if (lower.includes("hot") || lower.includes("cold")) return "parameter:temperature";
  if (lower.includes("dt") || lower.includes("delta")) return "parameter:dT";
  if (lower.includes("level")) return "parameter:level";
  return "parameter:temperature";
};

class Needs {
  namespaces = new Set<string>();
  getField = false;
  getCustomField = false;
  fieldTooltip = true;
  controllers = new Set<string>();
  exchangeCircuitConst: string | null = null;
  tankConst: string | null = null;
  heatExchangerPortOrientation = false;
}

const renderField = (fieldType: string, module: string, field: string, needs: Needs): string => {
  const enumInfo = FIELD_TYPE_TO_ENUM[fieldType];
  if (!enumInfo) throw new Error(`Unknown field type: ${fieldType} (${module}.${field})`);
  needs.namespaces.add(enumInfo.namespace);
  needs.getField = true;
  return `getField(${enumInfo.namespace}.${enumInfo.member}, "${module}", "${field}")`;
};

const renderCustom = (row: FillInRow, needs: Needs): string => {
  needs.getCustomField = true;
  const props: string[] = [];
  if (row.customTitle !== "") props.push(`title: "${escapeString(row.customTitle)}"`);
  if (row.customYardTag !== "") props.push(`yardTag: "${escapeString(row.customYardTag)}"`);
  if (row.customTechnicalName !== "")
    props.push(`technicalName: "${escapeString(row.customTechnicalName)}"`);
  if (props.length === 0) return `getCustomField("${row.sourceModule}")`;
  return `getCustomField("${row.sourceModule}", {\n      ${props.join(",\n      ")},\n    })`;
};

const renderCustomEntry = (
  row: FillInRow,
  needs: Needs,
): { code: string; needsGetter?: string } => {
  const key = slotKey(row.slotId);
  const value = row.valueKind;

  if (value === "literal") {
    return { code: `${key}: "${escapeString(row.literalValue)}"` };
  }

  if (value === "enum") {
    needs.heatExchangerPortOrientation = true;
    const member = row.refTarget.replace("enum:", "").split(".").pop() ?? "";
    return { code: `${key}: HeatExchangerPortOrientation.${member}` };
  }

  if (key === "exchangeCircuit") {
    needs.exchangeCircuitConst =
      needs.exchangeCircuitConst ?? `${moduleUpper(row.module)}_EXCHANGE_CIRCUIT_DATA`;
    return {
      code: `get exchangeCircuit() {\n      return ${needs.exchangeCircuitConst}[MimicComponentType.ExchangeCircuit].${row.refTarget}.sensors;\n    }`,
    };
  }

  if (key === "tankController") {
    needs.tankConst = needs.tankConst ?? `${moduleUpper(row.module)}_TANK_DATA`;
    return {
      code: `get tankController() {\n      return ${needs.tankConst}[MimicComponentType.BoilerTank]["${row.refTarget}"];\n    }`,
    };
  }

  needs.controllers.add(row.refTarget);
  return { code: `${key}: ${row.refTarget}` };
};

const renderSectionEntry = (row: FillInRow, needs: Needs): string => {
  if (row.valueKind === "field") {
    return `${slotKey(row.slotId)}: ${renderField(row.fieldType, row.sourceModule, row.fieldName, needs)}`;
  }
  if (row.valueKind === "ref") {
    needs.controllers.add(row.refTarget);
    return `${slotKey(row.slotId)}: ${row.refTarget}`;
  }
  throw new Error(`Unsupported value kind '${row.valueKind}' for slot ${row.slotId}`);
};

const renderTooltip = (row: FillInRow): string => {
  const props: string[] = [];
  if (row.tooltipTitle !== "") props.push(`title: "${escapeString(row.tooltipTitle)}"`);
  if (row.tooltipComponentType !== "")
    props.push(`componentType: "${escapeString(row.tooltipComponentType)}"`);
  if (row.tooltipTechnicalName !== "")
    props.push(`technicalName: "${escapeString(row.tooltipTechnicalName)}"`);
  const content = props.length > 0 ? `, {\n      ${props.join(",\n      ")},\n    }` : "";
  return `get tooltip() {\n    return fieldTooltip(this.source${content});\n  }`;
};

const renderInstanceFile = (instance: InstanceBuild, needs: Needs): string => {
  const bySection = groupBy(instance.rows, (r) => sectionOfSlot(r.slotId));
  const renderSection = (name: string): string | null => {
    const rows = bySection.get(name);
    if (!rows) return null;
    if (name === "source") {
      const row = rows[0];
      const value =
        row.valueKind === "field"
          ? renderField(row.fieldType, row.sourceModule, row.fieldName, needs)
          : renderCustom(row, needs);
      return `  source: ${value}`;
    }
    const entries: string[] = [];
    for (const row of rows) {
      if (name === "custom") {
        const { code } = renderCustomEntry(row, needs);
        entries.push(code);
      } else {
        entries.push(renderSectionEntry(row, needs));
      }
    }
    return `  ${name}: {\n${entries.map((e) => `    ${e}`).join(",\n")},\n  }`;
  };

  const body: string[] = [];
  for (const section of [
    "custom",
    "controls",
    "controllerState",
    "parameters",
    "source",
    "sensors",
  ]) {
    const rendered = renderSection(section);
    body.push(rendered ?? `  ${section}: {}`);
  }
  body.push(`  ${renderTooltip(instance.rows[0])}`);

  const imports = renderImports(needs);
  return `${imports}\nexport default toInstance<MimicComponentType.${instance.componentType}>({\n${body.join(",\n")},\n});\n`;
};

const renderImports = (needs: Needs): string => {
  const lines: string[] = [];
  const thrsim = [...needs.namespaces].sort();
  if (thrsim.length > 0) {
    lines.push(`import { ${thrsim.join(", ")} } from "@/modules/thrsim/types";`);
  }
  lines.push(`import { toInstance } from "../../..";`);
  lines.push(`import { MimicComponentType } from "../../../../../types";`);
  lines.push("");

  const secondGroup: string[] = [];
  const providerNames: string[] = [];
  if (needs.getField) providerNames.push("getField");
  if (needs.getCustomField) providerNames.push("getCustomField");
  if (providerNames.length > 0)
    secondGroup.push(`import { ${providerNames.join(", ")} } from "../../../../providers";`);
  secondGroup.push(`import { fieldTooltip } from "../../../shared";`);
  if (needs.controllers.size > 0) {
    secondGroup.push(
      `import { ${[...needs.controllers].sort().join(", ")} } from "../controllers";`,
    );
  }
  if (needs.exchangeCircuitConst) {
    secondGroup.push(`import { ${needs.exchangeCircuitConst} } from "..";`);
  }
  if (needs.tankConst) {
    secondGroup.push(`import { ${needs.tankConst} } from "../boiler-tanks";`);
  }
  if (needs.heatExchangerPortOrientation) {
    secondGroup.push(
      `import { HeatExchangerPortOrientation } from "../../../../components/heat-exchanger";`,
    );
  }
  lines.push(secondGroup.join("\n"));
  return lines.join("\n");
};

const collectControllers = (instances: InstanceBuild[]): ControllerDef[] => {
  const byName = new Map<string, ControllerDef>();
  for (const instance of instances) {
    for (const row of instance.rows) {
      if (row.pidControllerField === "" || row.valueKind !== "ref") continue;
      const existing = byName.get(row.refTarget);
      const def: ControllerDef = {
        name: row.refTarget,
        pidType: row.pidType === "flow" ? "flow" : "temperature",
        module: row.module,
        controllerField: row.pidControllerField,
        setpointField: row.pidSetpointField !== "" ? row.pidSetpointField : undefined,
        outputMinimumField:
          row.pidOutputMinimumField !== "" ? row.pidOutputMinimumField : undefined,
      };
      byName.set(row.refTarget, existing ?? def);
    }
  }
  return [...byName.values()].sort((a, b) => a.name.localeCompare(b.name));
};

const renderControllersFile = (controllers: ControllerDef[], module: string): string => {
  const blocks: string[] = [];
  for (const controller of controllers) {
    const sensorMember = controller.pidType === "flow" ? "Flow" : "Temperature";
    const lines: string[] = [
      `export const ${controller.name}: PIDController<SensorComponentType.${sensorMember}> = {`,
      `  type: SensorComponentType.${sensorMember},`,
      `  controller: getField(ControllerStateComponentType.PIDController, "${module}", "${controller.controllerField}"),`,
    ];
    if (controller.setpointField) {
      lines.push(
        `  setpoint: getField(ParametersType.${paramMemberOf(inferParameterFieldType(controller.setpointField))}, "${module}", "${controller.setpointField}"),`,
      );
    }
    if (controller.outputMinimumField) {
      lines.push(
        `  outputMinimum: getField(ParametersType.${paramMemberOf(inferParameterFieldType(controller.outputMinimumField))}, "${module}", "${controller.outputMinimumField}"),`,
      );
    }
    lines.push("};");
    blocks.push(lines.join("\n"));
  }
  return `import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrsim/types";

${blocks.join("\n\n")}\n`;
};

const renderFolderIndex = (module: string, folder: string, instances: InstanceBuild[]): string => {
  const byType = groupBy(instances, (i) => i.componentType);
  const imports = instances
    .map((i) => `import ${fileBase(i.key)} from "./${fileBase(i.key)}";`)
    .join("\n");
  const constName = folderConst(module, folder);
  const body = [...byType.entries()]
    .map(
      ([type, list]) =>
        `  [MimicComponentType.${type}]: {\n${list
          .map((i) => `    "${i.key}": ${fileBase(i.key)},`)
          .join("\n")}\n  }`,
    )
    .join(",\n");
  return `import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
${imports}

export const ${constName} = toFieldsMap({
${body},
});
`;
};

const renderDataIndex = (module: string, folderConsts: [string, string][]): string => {
  const imports = folderConsts
    .map(([constName, folder]) => `import { ${constName} } from "./${folder}";`)
    .join("\n");
  const reExports = folderConsts
    .map(([constName, folder]) => `export { ${constName} } from "./${folder}";`)
    .join("\n");
  const spread = folderConsts.map(([constName]) => `  ...${constName},`).join("\n");
  return `import { toFieldsMap } from "../..";
${imports}

${reExports}

export const ${moduleUpper(module)}_MIMIC_DATA = toFieldsMap({
${spread}
});
`;
};

const validateField = (row: FillInRow, schema: Map<string, SchemaRow>): void => {
  if (row.valueKind !== "field" || row.fieldName === "") return;
  const key = `${row.sourceModule}:${row.slotId.startsWith("controls") ? "controlValues" : row.slotId.startsWith("parameters") ? "parameters" : row.slotId.startsWith("controllerState") ? "controllerState" : "sensorValues"}:${row.fieldName}`;
  const schemaRow = schema.get(key);
  if (!schemaRow) {
    console.warn(`⚠️  No schema row for ${key}`);
    return;
  }
  if (schemaRow.componentType !== row.fieldType) {
    console.warn(
      `⚠️  Type mismatch for ${row.sourceModule}.${row.fieldName}: expected ${row.fieldType}, schema says ${schemaRow.componentType}`,
    );
  }
};

export const generateMimicModule = (
  fillInRecords: Record<string, string>[],
  outRoot: string,
  module: string,
  schemaRows?: SchemaRow[],
): number => {
  const rows = fillInRecords.map(toFillInRow);
  const instances = [
    ...groupBy(rows, (r) => `${r.module}\u0000${r.folder}\u0000${r.instanceKey}`).entries(),
  ]
    .filter(([key]) => key.startsWith(`${module}\u0000`))
    .map(([, list]) => {
      const first = list[0];
      const instance: InstanceBuild = {
        module: first.module,
        folder: first.folder,
        key: first.instanceKey,
        componentType: first.componentType,
        title: first.title,
        tooltipTitle: first.tooltipTitle,
        tooltipComponentType: first.tooltipComponentType,
        tooltipTechnicalName: first.tooltipTechnicalName,
        rows: list.filter(hasValue),
      };
      return instance;
    });

  if (instances.length === 0) {
    console.log(`No instances found for module '${module}'`);
    return 0;
  }

  const schema = new Map<string, SchemaRow>();
  if (schemaRows) {
    for (const row of schemaRows) {
      schema.set(`${row.module}:${row.section}:${row.field}`, row);
    }
    for (const instance of instances) {
      for (const row of instance.rows) validateField(row, schema);
    }
  }

  const controllers = collectControllers(instances);
  const moduleDataDir = path.join(outRoot, module, "data");

  const byFolder = groupBy(instances, (i) => i.folder);
  const folderConsts: [string, string][] = [];

  for (const [folder, folderInstances] of byFolder) {
    const folderDir = path.join(moduleDataDir, folder);
    mkdirSync(folderDir, { recursive: true });
    const generatedBases = new Set(folderInstances.map((i) => fileBase(i.key)));
    for (const file of readdirSync(folderDir)) {
      if (/^_.*\.ts$/.test(file) && !generatedBases.has(file.replace(/\.ts$/, ""))) {
        rmSync(path.join(folderDir, file));
      }
      if (file === "shared.ts") rmSync(path.join(folderDir, file));
    }
    for (const instance of folderInstances) {
      const needs = new Needs();
      const content = renderInstanceFile(instance, needs);
      writeFileSync(path.join(folderDir, `${fileBase(instance.key)}.ts`), content, "utf8");
    }
    const constName = folderConst(module, folder);
    writeFileSync(
      path.join(folderDir, "index.ts"),
      renderFolderIndex(module, folder, folderInstances),
      "utf8",
    );
    folderConsts.push([constName, folder]);
  }

  if (controllers.length > 0) {
    const controllersDir = path.join(moduleDataDir, "controllers");
    mkdirSync(controllersDir, { recursive: true });
    writeFileSync(
      path.join(controllersDir, "index.ts"),
      renderControllersFile(controllers, module),
      "utf8",
    );
  }

  writeFileSync(
    path.join(moduleDataDir, "index.ts"),
    renderDataIndex(module, folderConsts),
    "utf8",
  );

  console.log(
    `✓ generated ${module}: ${instances.length} instances in ${byFolder.size} folders, ${controllers.length} controllers`,
  );
  return instances.length;
};
