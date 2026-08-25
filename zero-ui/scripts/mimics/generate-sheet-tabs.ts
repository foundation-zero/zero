#!/usr/bin/env node

import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { writeCsv } from "./lib/csv";
import { parseModuleData } from "./lib/data-parser";
import { parseSchemaCatalog, toCatalogRow } from "./lib/schema";
import { instancesToFillIn, toInstancesRow } from "./lib/sheet-tabs";
import { deriveTemplates, toTemplateRow } from "./lib/templates";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SCHEMA_PATH = path.join(__dirname, "../../src/modules/thrsim/graphql/schema.graphql");
const MODULES_DIR = path.join(__dirname, "../../src/modules/thrapp/mimics/modules");
const OUT_DIR = path.join(__dirname, "mimic-out");

const main = (): void => {
  mkdirSync(OUT_DIR, { recursive: true });

  const schemaRows = parseSchemaCatalog(SCHEMA_PATH);
  writeCsv(path.join(OUT_DIR, "schema-catalog.csv"), schemaRows.map(toCatalogRow));
  console.log(`✓ schema-catalog.csv (${schemaRows.length} rows)`);

  const modules = ["dhw", "thrusters"].map((module) =>
    parseModuleData(path.join(MODULES_DIR, module), module),
  );

  const allInstances = modules.flatMap((m) => m.instances);
  writeCsv(path.join(OUT_DIR, "instances.csv"), allInstances.map(toInstancesRow));
  console.log(`✓ instances.csv (${allInstances.length} rows)`);

  const fillIn = instancesToFillIn(allInstances);
  writeCsv(path.join(OUT_DIR, "fillin-seed.csv"), fillIn);
  console.log(`✓ fillin-seed.csv (${fillIn.length} rows)`);

  const templates = deriveTemplates(modules);
  writeCsv(path.join(OUT_DIR, "component-templates.csv"), templates.map(toTemplateRow));
  console.log(`✓ component-templates.csv (${templates.length} rows)`);

  console.log(`Output written to ${OUT_DIR}`);
};

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
