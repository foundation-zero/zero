#!/usr/bin/env node

import path from "node:path";
import { fileURLToPath } from "node:url";
import { readCsv } from "./lib/csv";
import { generateMimicModule } from "./lib/generate";
import { parseSchemaCatalog } from "./lib/schema";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DEFAULT_MODULES_DIR = path.join(__dirname, "../../src/modules/thrapp/mimics/modules");
const SCHEMA_PATH = path.join(__dirname, "../../src/modules/thrsim/graphql/schema.graphql");

const main = (): void => {
  const args = process.argv.slice(2);
  const fillInPath = args[0];
  if (!fillInPath) {
    console.error("Usage: pnpm generate-mimic-data <path-to-fillin.csv> [module] [outRoot]");
    process.exit(1);
  }

  const module = args[1] ?? "";
  const outRoot = args[2] ? path.resolve(args[2]) : DEFAULT_MODULES_DIR;

  const fillInRecords = readCsv(path.resolve(fillInPath));
  const schemaRows = parseSchemaCatalog(SCHEMA_PATH);

  const modules = module !== "" ? [module] : [...new Set(fillInRecords.map((r) => r.module ?? ""))];

  let total = 0;
  for (const mod of modules) {
    total += generateMimicModule(fillInRecords, outRoot, mod, schemaRows);
  }
  console.log(`Done. Wrote ${total} instances under ${outRoot}`);
};

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
