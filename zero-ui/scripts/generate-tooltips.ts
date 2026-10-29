import { mkdir, mkdtemp, readdir, readFile, rm, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { isDeepStrictEqual } from "node:util";
import { build } from "vite";

type TooltipData = {
  source?: [string, string, string, unknown?];
  tooltip?: { yardTag?: string };
};

type ModuleData = Record<string, Record<string, TooltipData>>;

const root = fileURLToPath(new URL("..", import.meta.url));
const dataPath = join(root, "src/modules/thrapp/mimics/data");
const outputPath = join(dataPath, "tooltips.json");

const stripData = <T>(data: T): Partial<T> => {
  const copy = JSON.parse(JSON.stringify(data));

  return Object.fromEntries(
    Object.entries(copy).filter(
      ([_, value]) =>
        value != null &&
        (typeof value != "object" || Array.isArray(value) || Object.keys(value).length > 0),
    ),
  ) as Partial<T>;
};

const moduleNames = (await readdir(dataPath, { withFileTypes: true }))
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
const modulePaths: Record<string, string> = {};

for (const module of moduleNames) {
  const modulePath = join(dataPath, module);
  const files = await readdir(modulePath);
  if (files.includes("index.ts")) modulePaths[module] = join(modulePath, "index.ts");
}

const temporaryRoot = join(root, "node_modules/.tmp");
await mkdir(temporaryRoot, { recursive: true });
const temporaryDirectory = await mkdtemp(join(temporaryRoot, "tooltip-data-"));

try {
  const entryId = "\0tooltip-data-entry";
  const result = await build({
    configFile: false,
    root,
    logLevel: "error",
    resolve: { alias: { "@": join(root, "src"), "@env": join(root, "src/settings/index.ts") } },
    plugins: [
      {
        name: "tooltip-data-only",
        resolveId(id) {
          if (id === entryId) return id;
        },
        load(id) {
          if (id.endsWith(".vue")) return "export default {};";
          if (id === entryId) {
            return Object.entries(modulePaths)
              .map(
                ([module, path]) =>
                  `export { ${module.toUpperCase()}_MIMIC_DATA as ${module} } from ${JSON.stringify(path)};`,
              )
              .join("\n");
          }
        },
      },
    ],
    build: {
      ssr: true,
      write: false,
      minify: false,
      rolldownOptions: { input: entryId, output: { format: "cjs", codeSplitting: false } },
    },
  });
  if (Array.isArray(result) || !("output" in result))
    throw new Error("Expected a single data bundle");
  const chunk = result.output.find((output) => output.type === "chunk" && output.isEntry);
  if (!chunk || chunk.type !== "chunk") throw new Error("No tooltip data bundle generated");
  const bundlePath = join(temporaryDirectory, "data.cjs");
  await writeFile(bundlePath, chunk.code);
  const modules = createRequire(import.meta.url)(bundlePath) as Record<string, ModuleData>;
  const register: Record<string, string> = {};
  const contexts: Record<string, Record<string, TooltipData | TooltipData[]>> = {};
  const entries: {
    key: string;
    registerKeys: string[];
    componentType: string;
    context: TooltipData;
  }[] = [];

  for (const [module, data] of Object.entries(modules)) {
    for (const [componentType, instances] of Object.entries(data)) {
      for (const [instance, context] of Object.entries(instances)) {
        const resolved = stripData(context);
        const source = resolved.source;
        const isNamed = !/^\d+(?:-\d+)*$/.test(instance);
        const hasYardTag = Boolean(resolved.tooltip?.yardTag) || !isNamed;
        const yardTag = resolved.tooltip?.yardTag || (isNamed ? `${module}:${instance}` : instance);
        if (yardTag && resolved.tooltip) resolved.tooltip.yardTag = yardTag;
        // Named instances (e.g. circuits) can share a yard tag with another module's view of the
        // same component, so key them by name to keep their contexts apart.
        const key =
          (isNamed ? `${module}:${instance}` : yardTag) || (source && `${source[1]}/${source[2]}`);
        if (!key) throw new Error(`Tooltip in ${module} has neither a yardTag nor a source`);
        entries.push({
          key,
          registerKeys:
            !source || source[0] === "custom" || source[2] === "placeholder"
              ? []
              : hasYardTag
                ? [instance, `${module}:${source?.[2]}`]
                : [`${module}:${instance}`],
          componentType,
          context: resolved,
        });
      }
    }
  }

  // A named instance's bare name (e.g. "domesticHotWater") can be used by several modules, so it
  // only becomes an alias when it points at a single context; otherwise the first module alphabetically
  // would silently claim it.
  const aliasTargets = new Map<string, Set<string>>();
  for (const entry of entries) {
    for (const registerKey of entry.registerKeys) {
      const targets = aliasTargets.get(registerKey) ?? new Set();
      aliasTargets.set(registerKey, targets.add(`${entry.componentType}/${entry.key}`));
    }
  }
  const isAmbiguous = (registerKey: string) =>
    !/^\d+(?:-\d+)*$/.test(registerKey) &&
    !registerKey.includes(":") &&
    aliasTargets.get(registerKey)!.size > 1;

  let redundant = 0;
  for (const entry of entries) {
    for (const registerKey of entry.registerKeys) {
      if (!Object.hasOwn(register, registerKey) && !isAmbiguous(registerKey)) {
        register[registerKey] = `${entry.componentType}/${entry.key}`;
      }
    }
    const group = (contexts[entry.componentType] ??= {});
    const existing = Object.hasOwn(group, entry.key) ? group[entry.key] : undefined;
    if (
      existing !== undefined &&
      (Array.isArray(existing) ? existing : [existing]).some((context) =>
        isDeepStrictEqual(context, entry.context),
      )
    ) {
      redundant++;
      continue;
    }
    if (existing === undefined) {
      group[entry.key] = entry.context;
    } else if (Array.isArray(existing)) {
      existing.push(entry.context);
    } else {
      group[entry.key] = [existing, entry.context];
    }
  }
  const total = entries.length - redundant;
  const duplicates = Object.values(contexts)
    .flatMap((group) => Object.values(group))
    .filter(Array.isArray).length;

  const sortedData = {
    register: Object.fromEntries(
      Object.entries(register).sort(([left], [right]) => left.localeCompare(right)),
    ),
    contexts: Object.fromEntries(
      Object.entries(contexts)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([componentType, group]) => [
          componentType,
          Object.fromEntries(
            Object.entries(group).sort(([left], [right]) => left.localeCompare(right)),
          ),
        ]),
    ),
  };
  const json = `${JSON.stringify(sortedData, null, 2)}\n`;
  if (process.argv.includes("--check")) {
    if ((await readFile(outputPath, "utf8")) !== json)
      throw new Error("tooltips.json is out of date; run pnpm generate-tooltips");
    console.log(
      `Verified ${total} tooltip records (${duplicates} duplicate-key arrays, ${redundant} identical duplicates removed)`,
    );
  } else {
    await mkdir(dirname(outputPath), { recursive: true });
    await writeFile(outputPath, json);
    console.log(
      `Generated ${total} tooltip records (${duplicates} duplicate-key arrays, ${redundant} identical duplicates removed) in ${outputPath}`,
    );
  }
} finally {
  await rm(temporaryDirectory, { recursive: true, force: true });
}
