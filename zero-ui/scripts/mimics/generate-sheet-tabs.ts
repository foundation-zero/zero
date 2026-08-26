#!/usr/bin/env node

import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { writeCsv } from "./lib/csv";
import { parseModuleData } from "./lib/data-parser";
import { parseSchemaCatalog, toCatalogRow } from "./lib/schema";
import {
  controllerHeaders,
  instanceHeaders,
  instancesToPlanRows,
  planHeaders,
  toControllersRows,
  toInstancesRow,
} from "./lib/sheet-tabs";
import { templateRows, toTemplateRow } from "./lib/templates";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SCHEMA_PATH = path.join(__dirname, "../../src/modules/thrsim/graphql/schema.graphql");
const MODULES_DIR = path.join(__dirname, "../../src/modules/thrapp/mimics/modules");
const OUT_DIR = path.join(__dirname, "mimic-out");

const SEED_MODULES = ["dhw", "thrusters"];

const main = (): void => {
  mkdirSync(OUT_DIR, { recursive: true });

  const schemaRows = parseSchemaCatalog(SCHEMA_PATH);
  writeCsv(path.join(OUT_DIR, "schema-catalog.csv"), schemaRows.map(toCatalogRow));
  console.log(`✓ schema-catalog.csv (${schemaRows.length} rows)`);

  writeCsv(path.join(OUT_DIR, "component-templates.csv"), templateRows().map(toTemplateRow));
  console.log(`✓ component-templates.csv (${templateRows().length} rows)`);

  const modules = SEED_MODULES.map((module) =>
    parseModuleData(path.join(MODULES_DIR, module), module),
  );

  const allInstances = modules.flatMap((m) => m.instances);
  writeCsv(
    path.join(OUT_DIR, "instances.csv"),
    allInstances
      .map(toInstancesRow)
      .map((row) => Object.fromEntries(instanceHeaders.map((header) => [header, row[header]]))),
  );
  console.log(`✓ instances.csv (${allInstances.length} rows)`);

  const controllers = toControllersRows(modules);
  writeCsv(
    path.join(OUT_DIR, "controllers-seed.csv"),
    controllers.map((row) =>
      Object.fromEntries(controllerHeaders.map((header) => [header, row[header]])),
    ),
  );
  console.log(`✓ controllers-seed.csv (${controllers.length} rows)`);

  const fieldModules = new Map<string, Set<string>>();
  for (const row of schemaRows) {
    if (!fieldModules.has(row.field)) fieldModules.set(row.field, new Set());
    fieldModules.get(row.field)?.add(row.module);
  }
  const planSeed = instancesToPlanRows(allInstances, fieldModules);
  writeCsv(
    path.join(OUT_DIR, "plan-seed.csv"),
    planSeed.map((row) => Object.fromEntries(planHeaders.map((header) => [header, row[header]]))),
  );
  console.log(`✓ plan-seed.csv (${planSeed.length} rows)`);

  console.log(`Output written to ${OUT_DIR}`);
};

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
