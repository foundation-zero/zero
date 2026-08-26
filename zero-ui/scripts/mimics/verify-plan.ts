#!/usr/bin/env node

import path from "node:path";
import { fileURLToPath } from "node:url";
import { readCsv } from "./lib/csv";
import { parseModuleData } from "./lib/data-parser";
import { parseSchemaCatalog } from "./lib/schema";
import { instancesToPlanRows, planHeaders } from "./lib/sheet-tabs";
import { canonicalSlotsOf } from "./lib/templates";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SCHEMA_PATH = path.join(__dirname, "../../src/modules/thrsim/graphql/schema.graphql");
const MODULES_DIR = path.join(__dirname, "../../src/modules/thrapp/mimics/modules");

const ENUM_MEMBERS = new Set(["Side", "Top"]);
const DESIGNER_COLUMNS = ["value", "srcTitle", "srcYardTag"] as const;

const usage = (): never => {
  console.error(
    "Usage:\n" +
      "  pnpm verify-plan <plan.csv> [controllers.csv]        validate a filled plan export\n" +
      "  pnpm verify-plan --check <plan.csv>                  validate + diff against committed mimic data",
  );
  process.exit(1);
};

const isEmptyContent = (row: Record<string, string>): boolean =>
  DESIGNER_COLUMNS.every((column) => (row[column] ?? "").trim() === "");

interface CatalogIndex {
  byField: Map<string, { module: string; componentType: string }[]>;
}

const buildCatalogIndex = (): CatalogIndex => {
  const index: CatalogIndex = { byField: new Map() };
  for (const row of parseSchemaCatalog(SCHEMA_PATH)) {
    const entries = index.byField.get(row.field) ?? [];
    entries.push({ module: row.module, componentType: row.componentType });
    index.byField.set(row.field, entries);
  }
  return index;
};

class Reporter {
  private errors = 0;

  error(message: string): void {
    this.errors += 1;
    console.error(`❌ ${message}`);
  }

  warn(message: string): void {
    console.warn(`⚠️  ${message}`);
  }

  finish(): void {
    if (this.errors > 0) {
      console.error(`❌ ${this.errors} problem(s) found`);
      process.exit(1);
    }
    console.log("✅ Plan OK");
  }
}

const resolveFieldValue = (
  raw: string,
  instanceModule: string,
  allowedTypes: string[],
  catalog: CatalogIndex,
  reporter: Reporter,
  label: string,
): void => {
  let moduleName = "";
  let field = raw.trim();
  const prefixSplit = field.split(":");
  if (prefixSplit.length === 2) {
    [moduleName, field] = prefixSplit;
  }
  const candidates = (catalog.byField.get(field) ?? []).filter(
    (candidate) => moduleName === "" || candidate.module === moduleName,
  );
  if (candidates.length === 0) {
    reporter.error(`${label}: unknown datapoint '${raw}'`);
    return;
  }
  const compatible = candidates.filter((candidate) =>
    allowedTypes.includes(candidate.componentType),
  );
  if (compatible.length === 0) {
    reporter.error(
      `${label}: '${raw}' has type ${candidates[0].componentType}, expected one of ${allowedTypes.join("|")}`,
    );
    return;
  }
  if (!moduleName && candidates.some((candidate) => candidate.module !== instanceModule)) {
    reporter.warn(
      `${label}: '${raw}' exists in multiple modules (${candidates.map((c) => c.module).join(", ")}) — qualify as 'module:${field}'`,
    );
  }
};

const validateRow = (
  row: Record<string, string>,
  controllerNames: Set<string> | undefined,
  instanceKeysByModule: Map<string, Set<string>>,
  allInstanceKeys: Set<string>,
  catalog: CatalogIndex,
  reporter: Reporter,
): void => {
  const label = `${row.module}/${row.folder}/${row.key} · ${row.slotId}`;
  const templates = canonicalSlotsOf(row.componentType);
  if (templates.length === 0) {
    reporter.error(`${label}: unknown componentType '${row.componentType}'`);
    return;
  }
  const template = templates.find((entry) => entry.slotId === row.slotId);
  if (!template) {
    reporter.error(`${label}: slotId not defined for ${row.componentType}`);
    return;
  }

  const content = DESIGNER_COLUMNS.map((column) => row[column]?.trim() ?? "").join("|");
  if (template.required && content === "||") {
    reporter.error(`${label}: required slot is empty`);
    return;
  }
  if (content === "||") return;

  switch (template.valueKind) {
    case "field": {
      const controllerMatch = row.value.match(/^@controller:(.+)$/);
      if (controllerMatch) {
        if (controllerNames && !controllerNames.has(controllerMatch[1])) {
          reporter.error(`${label}: unknown controller '${controllerMatch[1]}'`);
        }
        break;
      }
      resolveFieldValue(row.value, row.module, template.fieldTypes ?? [], catalog, reporter, label);
      break;
    }
    case "customSource":
      if (!row.srcTitle) reporter.warn(`${label}: no srcTitle given for source row`);
      if (!row.value)
        reporter.error(`${label}: value (technical name slug) is required for source rows`);
      break;
    case "literal":
      if (!row.value) reporter.error(`${label}: value must contain the text`);
      break;
    case "enum":
      if (!ENUM_MEMBERS.has(row.value))
        reporter.error(`${label}: enum value '${row.value}' must be one of Side|Top`);
      break;
    case "controllerRef": {
      const match = row.value.match(/^@controller:(.+)$/);
      if (!match) {
        reporter.error(`${label}: expected '@controller:<name>', got '${row.value}'`);
        break;
      }
      if (controllerNames && !controllerNames.has(match[1])) {
        reporter.error(`${label}: unknown controller '${match[1]}'`);
      }
      break;
    }
    case "instanceRef": {
      const match = row.value.match(/^@instance:(.+)$/);
      if (!match) {
        reporter.error(`${label}: expected '@instance:<key>', got '${row.value}'`);
        break;
      }
      const key = match[1];
      if (!instanceKeysByModule.get(row.module)?.has(key) && !allInstanceKeys.has(key)) {
        reporter.error(`${label}: no instance with key '${key}' in the plan`);
      }
      break;
    }
  }
};

const collectControllerNames = (path: string | undefined): Set<string> | undefined => {
  if (!path) return undefined;
  const names = new Set<string>();
  for (const row of readCsv(path)) {
    if (row.name) names.add(row.name);
  }
  return names;
};

const planKey = (row: Record<string, string>): string =>
  `${row.module}|${row.folder}|${row.key}|${row.slotId}`;

const fieldModulesFromCatalog = (): Map<string, Set<string>> => {
  const fieldModules = new Map<string, Set<string>>();
  for (const row of parseSchemaCatalog(SCHEMA_PATH)) {
    if (!fieldModules.has(row.field)) fieldModules.set(row.field, new Set());
    fieldModules.get(row.field)?.add(row.module);
  }
  return fieldModules;
};

const diffAgainstCode = (
  rows: Record<string, string>[],
  fieldModules: Map<string, Set<string>>,
): void => {
  const modules = [...new Set(rows.map((row) => row.module))];
  const committedInstances = modules.flatMap(
    (module) => parseModuleData(path.join(MODULES_DIR, module), module).instances,
  );
  const expectedRows = instancesToPlanRows(committedInstances, fieldModules).filter(
    (row) => !isEmptyContent(row),
  );

  const actual = new Map(
    rows.filter((row) => !isEmptyContent(row)).map((row) => [planKey(row), row]),
  );
  const expected = new Map(expectedRows.map((row) => [planKey(row), row]));

  let differences = 0;
  for (const [key, row] of expected) {
    const other = actual.get(key);
    if (!other) {
      differences += 1;
      console.error(`❌ missing in sheet: ${key.replaceAll("|", "/")}`);
    } else if (DESIGNER_COLUMNS.some((column) => (other[column] ?? "") !== (row[column] ?? ""))) {
      differences += 1;
      console.error(
        `❌ mismatch ${key.replaceAll("|", "/")}: sheet=[${DESIGNER_COLUMNS.map((c) => other[c]).join(", ")}] code=[${DESIGNER_COLUMNS.map((c) => row[c]).join(", ")}]`,
      );
    }
  }
  for (const key of actual.keys()) {
    if (!expected.has(key)) {
      differences += 1;
      console.error(`❌ in sheet but not in code: ${key.replaceAll("|", "/")}`);
    }
  }
  if (differences > 0) {
    console.error(`❌ Plan does not match committed data (${differences} difference(s))`);
    process.exit(1);
  }
  console.log(`✅ Plan matches committed data (${actual.size} filled rows)`);
};

const main = (): void => {
  const args = process.argv.slice(2);
  const check = args.includes("--check");
  const positional = args.filter((arg) => arg !== "--check");
  const planPath = positional[0];
  const controllersPath = positional[1];
  if (!planPath) usage();

  const reporter = new Reporter();
  const rows = readCsv(path.resolve(planPath));
  if (rows.length === 0) usage();
  const missingColumns = planHeaders.filter((header) => !(header in rows[0]));
  if (missingColumns.length > 0) {
    reporter.error(`Missing columns: ${missingColumns.join(", ")}`);
    process.exit(1);
  }

  const seen = new Set<string>();
  const instanceKeysByModule = new Map<string, Set<string>>();
  const allInstanceKeys = new Set<string>();
  for (const row of rows) {
    const key = `${row.module}/${row.key}`;
    allInstanceKeys.add(row.key);
    if (!instanceKeysByModule.has(row.module)) instanceKeysByModule.set(row.module, new Set());
    instanceKeysByModule.get(row.module)?.add(row.key);
    const dedupeKey = `${key}|${row.folder}|${row.slotId}`;
    if (seen.has(dedupeKey)) reporter.error(`Duplicate row: ${dedupeKey.replaceAll("|", "/")}`);
    seen.add(dedupeKey);
  }

  const controllerNames = collectControllerNames(
    controllersPath ? path.resolve(controllersPath) : undefined,
  );
  if (!controllerNames) {
    reporter.warn("No controllers CSV given — @controller: references are not checked");
  }

  const catalog = buildCatalogIndex();
  for (const row of rows) {
    validateRow(row, controllerNames, instanceKeysByModule, allInstanceKeys, catalog, reporter);
  }
  reporter.finish();

  if (check) diffAgainstCode(rows, fieldModulesFromCatalog());
};

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
