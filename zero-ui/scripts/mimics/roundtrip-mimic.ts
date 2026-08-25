#!/usr/bin/env node

import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseModuleData } from "./lib/data-parser";
import { generateMimicModule } from "./lib/generate";
import { parseSchemaCatalog } from "./lib/schema";
import { instancesToFillIn } from "./lib/sheet-tabs";
import { InstanceModel, SlotValue } from "./lib/types";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MODULES_DIR = path.join(__dirname, "../../src/modules/thrapp/mimics/modules");
const OUT_DIR = path.join(__dirname, "mimic-out/roundtrip");
const SCHEMA_PATH = path.join(__dirname, "../../src/modules/thrsim/graphql/schema.graphql");

const canonicalInstance = (instance: InstanceModel): string => {
  const slots = [...instance.slots]
    .sort((a, b) => a.slotId.localeCompare(b.slotId))
    .map((s) => `${s.slotId}=${JSON.stringify(canonicalSlot(s))}`);
  return JSON.stringify({
    componentType: instance.componentType,
    key: instance.key,
    tooltip: instance.tooltip ?? null,
    slots,
  });
};

const canonicalSlot = (slot: SlotValue): Record<string, unknown> => {
  const value: Record<string, unknown> = { ...slot.value };
  if (slot.pid) {
    value.pid = {
      pidType: slot.pid.pidType,
      controllerField: slot.pid.controllerField.field,
      setpoint: slot.pid.setpoint?.field,
      outputMinimum: slot.pid.outputMinimum?.field,
    };
  }
  return value;
};

const compareModule = (module: string): number => {
  const committed = parseModuleData(path.join(MODULES_DIR, module), module);
  const seed = instancesToFillIn(committed.instances);
  const generatedDir = path.join(OUT_DIR, module);
  mkdirSync(generatedDir, { recursive: true });

  const schemaRows = parseSchemaCatalog(SCHEMA_PATH);
  generateMimicModule(seed, OUT_DIR, module, schemaRows);

  const generated = parseModuleData(generatedDir, module);

  const committedCanon = new Map(
    committed.instances.map((i) => [`${i.componentType}:${i.key}`, canonicalInstance(i)]),
  );
  const generatedCanon = new Map(
    generated.instances.map((i) => [`${i.componentType}:${i.key}`, canonicalInstance(i)]),
  );

  let differences = 0;
  for (const [key, value] of committedCanon) {
    if (generatedCanon.get(key) !== value) {
      differences += 1;
      console.log(`❌ ${module} ${key} differs`);
    }
  }
  for (const [key] of generatedCanon) {
    if (!committedCanon.has(key)) {
      differences += 1;
      console.log(`❌ ${module} ${key} only in generated`);
    }
  }
  if (differences === 0) {
    console.log(`✅ ${module}: ${committed.instances.length} instances round-trip clean`);
  }
  return differences;
};

const main = (): void => {
  let failures = 0;
  for (const module of ["dhw", "thrusters"]) {
    failures += compareModule(module);
  }
  if (failures > 0) {
    console.error(`❌ Round-trip failed for ${failures} instance(s)`);
    process.exit(1);
  }
  console.log("✅ Round-trip OK");
};

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
