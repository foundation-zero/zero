import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import ts from "typescript";
import { NAMESPACE_TO_FIELD_TYPE } from "./enums";
import {
  FieldValue,
  InstanceModel,
  ModuleData,
  PidControllerDef,
  SlotKind,
  SlotValue,
  TooltipInfo,
} from "./types";

const fieldTypeOf = (dotted: string): string | null => {
  const [namespace, member] = dotted.split(".");
  return NAMESPACE_TO_FIELD_TYPE[namespace]?.[member] ?? null;
};

const createSource = (filePath: string): ts.SourceFile => {
  const text = readFileSync(filePath, "utf8");
  return ts.createSourceFile(filePath, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
};

const propName = (name: ts.PropertyName | undefined): string | null => {
  if (!name) return null;
  if (ts.isIdentifier(name) || ts.isStringLiteral(name) || ts.isNumericLiteral(name)) {
    return name.text;
  }
  return null;
};

const isGetField = (expr: ts.Expression): expr is ts.CallExpression =>
  ts.isCallExpression(expr) &&
  ts.isIdentifier(expr.expression) &&
  expr.expression.text === "getField";

const isGetCustomField = (expr: ts.Expression): expr is ts.CallExpression =>
  ts.isCallExpression(expr) &&
  ts.isIdentifier(expr.expression) &&
  expr.expression.text === "getCustomField";

const stringArg = (call: ts.CallExpression, index: number): string => {
  const arg = call.arguments[index];
  return arg && ts.isStringLiteral(arg) ? arg.text : "";
};

const parseFieldCall = (call: ts.CallExpression): Extract<FieldValue, { kind: "field" }> | null => {
  const first = call.arguments[0];
  if (!first || !ts.isPropertyAccessExpression(first)) return null;
  const fieldType = fieldTypeOf(`${first.expression.getText()}.${first.name.text}`);
  if (!fieldType) return null;
  return {
    kind: "field",
    fieldType,
    module: stringArg(call, 1),
    field: stringArg(call, 2),
  };
};

const parseCustomCall = (call: ts.CallExpression): Extract<FieldValue, { kind: "custom" }> => {
  const value: Extract<FieldValue, { kind: "custom" }> = {
    kind: "custom",
    module: stringArg(call, 0),
    technicalName: "",
  };
  const obj = call.arguments[1];
  if (obj && ts.isObjectLiteralExpression(obj)) {
    for (const prop of obj.properties) {
      if (ts.isPropertyAssignment(prop)) {
        const key = propName(prop.name);
        const text =
          prop.initializer && ts.isStringLiteral(prop.initializer)
            ? prop.initializer.text
            : undefined;
        if (key === "title" && text !== undefined) value.title = text;
        if (key === "yardTag" && text !== undefined) value.yardTag = text;
        if (key === "technicalName" && text !== undefined) value.technicalName = text;
      }
    }
  }
  return value;
};

const isExchangeCircuitChain = (expr: ts.Expression): boolean =>
  expr.getText().includes("MimicComponentType.ExchangeCircuit") &&
  expr.getText().trimEnd().endsWith(".sensors");

const instanceKeyFromChain = (expr: ts.Expression): string => {
  const text = expr.getText();
  const bracketMatch = text.match(/\]\["([^"]+)"\]\s*$/);
  if (bracketMatch) return bracketMatch[1];
  const dotMatch = text.match(/\]\.([A-Za-z0-9_-]+)\.sensors\s*$/);
  if (dotMatch) return dotMatch[1];
  return "";
};

const parseEnum = (expr: ts.Expression): Extract<FieldValue, { kind: "enum" }> | null => {
  if (ts.isPropertyAccessExpression(expr)) {
    const root = expr.expression;
    if (ts.isIdentifier(root) && root.text === "HeatExchangerPortOrientation") {
      return { kind: "enum", enumName: "HeatExchangerPortOrientation", member: expr.name.text };
    }
  }
  return null;
};

type SharedValue =
  | { kind: "field"; value: FieldValue }
  | { kind: "object"; entries: Record<string, FieldValue> }
  | { kind: "tooltip"; tooltip?: TooltipInfo };

const parseTooltipObject = (node: ts.Node): TooltipInfo | undefined => {
  let tooltip: TooltipInfo | undefined;
  const find = (n: ts.Node): void => {
    if (tooltip) return;
    if (
      ts.isCallExpression(n) &&
      ts.isIdentifier(n.expression) &&
      n.expression.text === "fieldTooltip"
    ) {
      const obj = n.arguments[1];
      if (obj && ts.isObjectLiteralExpression(obj)) {
        tooltip = {};
        for (const prop of obj.properties) {
          if (!ts.isPropertyAssignment(prop)) continue;
          const key = propName(prop.name);
          const text =
            prop.initializer && ts.isStringLiteral(prop.initializer)
              ? prop.initializer.text
              : undefined;
          if (!key || text === undefined) continue;
          if (key === "title") tooltip.title = text;
          if (key === "componentType") tooltip.componentType = text;
          if (key === "technicalName") tooltip.technicalName = text;
        }
      }
      return;
    }
    ts.forEachChild(n, find);
  };
  find(node);
  return tooltip;
};

export const parseSharedTs = (filePath: string): Map<string, SharedValue> => {
  const shared = new Map<string, SharedValue>();
  if (!existsSync(filePath)) return shared;
  const source = createSource(filePath);
  for (const statement of source.statements) {
    if (
      !ts.isVariableStatement(statement) ||
      !statement.modifiers?.some((m) => m.kind === ts.SyntaxKind.ExportKeyword)
    ) {
      continue;
    }
    for (const decl of statement.declarationList.declarations) {
      const name = ts.isIdentifier(decl.name) ? decl.name.text : "";
      const init = decl.initializer;
      if (!init) continue;
      if (isGetField(init) || isGetCustomField(init)) {
        const value = isGetField(init) ? parseFieldCall(init) : parseCustomCall(init);
        if (value) shared.set(name, { kind: "field", value });
      } else if (ts.isObjectLiteralExpression(init)) {
        const entries: Record<string, FieldValue> = {};
        for (const prop of init.properties) {
          if (ts.isPropertyAssignment(prop)) {
            const key = propName(prop.name);
            if (!key) continue;
            if (isGetField(prop.initializer)) {
              const v = parseFieldCall(prop.initializer);
              if (v) entries[key] = v;
            }
          } else if (
            (ts.isMethodDeclaration(prop) || ts.isGetAccessorDeclaration(prop)) &&
            prop.name.getText() === "tankController"
          ) {
            const ret = firstReturnExpr(prop.body);
            if (ret)
              entries.tankController = { kind: "ref", ref: instanceKeyFromChain(ret) || "tank" };
          }
        }
        shared.set(name, { kind: "object", entries });
      } else {
        const tooltip = parseTooltipObject(init);
        if (tooltip) shared.set(name, { kind: "tooltip", tooltip });
      }
    }
  }
  return shared;
};

const firstReturnExpr = (body: ts.Node | undefined): ts.Expression | undefined => {
  if (!body) return undefined;
  let found: ts.Expression | undefined;
  const visitNode = (n: ts.Node): void => {
    if (found) return;
    if (ts.isReturnStatement(n)) {
      found = n.expression;
      return;
    }
    ts.forEachChild(n, visitNode);
  };
  visitNode(body);
  return found;
};

export const parseControllersTs = (filePath: string): PidControllerDef[] => {
  if (!existsSync(filePath)) return [];
  const source = createSource(filePath);
  const controllers: PidControllerDef[] = [];
  for (const statement of source.statements) {
    if (!ts.isVariableStatement(statement)) continue;
    for (const decl of statement.declarationList.declarations) {
      const name = ts.isIdentifier(decl.name) ? decl.name.text : "";
      const init = decl.initializer;
      if (!init || !ts.isObjectLiteralExpression(init)) continue;
      const def: PidControllerDef = {
        name,
        pidType: "temperature",
        controllerField: { kind: "field", fieldType: "pidController", module: "", field: "" },
      };
      for (const prop of init.properties) {
        if (!ts.isPropertyAssignment(prop)) continue;
        const key = propName(prop.name);
        const value = prop.initializer;
        if (key === "type" && ts.isPropertyAccessExpression(value)) {
          def.pidType = value.name.text === "Flow" ? "flow" : "temperature";
        } else if (key === "controller" && isGetField(value)) {
          const parsed = parseFieldCall(value);
          if (parsed) def.controllerField = parsed;
        } else if (key === "setpoint" && isGetField(value)) {
          const parsed = parseFieldCall(value);
          if (parsed) def.setpoint = parsed;
        } else if (key === "outputMinimum" && isGetField(value)) {
          const parsed = parseFieldCall(value);
          if (parsed) def.outputMinimum = parsed;
        }
      }
      controllers.push(def);
    }
  }
  return controllers;
};

interface FolderIndex {
  filenameToKey: Record<string, string>;
  componentKeys: Record<string, string[]>;
}

export const parseFolderIndex = (filePath: string): FolderIndex => {
  const source = createSource(filePath);
  const filenameToKey: Record<string, string> = {};
  const componentKeys: Record<string, string[]> = {};
  const importLocalToFile = new Map<string, string>();
  for (const statement of source.statements) {
    if (!ts.isImportDeclaration(statement) || !ts.isStringLiteral(statement.moduleSpecifier)) {
      continue;
    }
    const spec = statement.moduleSpecifier.text;
    if (!spec.startsWith("./")) continue;
    const clause = statement.importClause;
    if (clause?.name && ts.isIdentifier(clause.name)) {
      importLocalToFile.set(clause.name.text, spec.replace(/^\.\//, "").replace(/\.ts$/, ""));
    }
  }
  let found = false;
  const visitNode = (n: ts.Node): void => {
    if (found) return;
    if (
      ts.isCallExpression(n) &&
      ts.isIdentifier(n.expression) &&
      n.expression.text === "toFieldsMap"
    ) {
      found = true;
      const obj = n.arguments[0];
      if (obj && ts.isObjectLiteralExpression(obj)) {
        for (const prop of obj.properties) {
          if (!ts.isPropertyAssignment(prop) || !ts.isComputedPropertyName(prop.name)) continue;
          const member = prop.name.expression;
          if (
            !ts.isPropertyAccessExpression(member) ||
            member.expression.getText() !== "MimicComponentType"
          )
            continue;
          const componentType = member.name.text;
          componentKeys[componentType] = [];
          const map = prop.initializer;
          if (map && ts.isObjectLiteralExpression(map)) {
            for (const entry of map.properties) {
              if (!ts.isPropertyAssignment(entry)) continue;
              const key = propName(entry.name);
              if (!key) continue;
              const local = ts.isIdentifier(entry.initializer) ? entry.initializer.text : "";
              const fileBaseName = importLocalToFile.get(local) ?? local;
              if (fileBaseName) filenameToKey[fileBaseName] = key;
              componentKeys[componentType].push(key);
            }
          }
        }
      }
      return;
    }
    ts.forEachChild(n, visitNode);
  };
  visitNode(source);
  return { filenameToKey, componentKeys };
};

interface SectionEntry {
  key: string;
  value: FieldValue;
  pid?: PidControllerDef;
}

const resolveIdentifier = (
  text: string,
  section: SlotKind,
  shared: Map<string, SharedValue>,
  controllersByName: Map<string, PidControllerDef>,
): { value?: FieldValue; pid?: PidControllerDef; objectEntries?: Record<string, FieldValue> } => {
  const sharedValue = shared.get(text);
  if (sharedValue) {
    if (sharedValue.kind === "field") return { value: sharedValue.value };
    if (sharedValue.kind === "object") return { objectEntries: sharedValue.entries };
  }
  const pid = controllersByName.get(text);
  if (pid) return { value: { kind: "ref", ref: text }, pid };
  throw new Error(`Unresolved identifier '${text}' in ${section} section`);
};

const resolveExpression = (
  expr: ts.Expression,
  section: SlotKind,
  shared: Map<string, SharedValue>,
  controllersByName: Map<string, PidControllerDef>,
): { value?: FieldValue; pid?: PidControllerDef; objectEntries?: Record<string, FieldValue> } => {
  if (isGetField(expr)) {
    const value = parseFieldCall(expr);
    if (value) return { value };
  }
  if (isGetCustomField(expr)) return { value: parseCustomCall(expr) };
  if (ts.isIdentifier(expr))
    return resolveIdentifier(expr.text, section, shared, controllersByName);
  if (ts.isStringLiteral(expr)) return { value: { kind: "literal", value: expr.text } };
  const enumValue = parseEnum(expr);
  if (enumValue) return { value: enumValue };
  if (isExchangeCircuitChain(expr))
    return { value: { kind: "ref", ref: instanceKeyFromChain(expr) } };
  throw new Error(`Unsupported expression in ${section}: ${expr.getText()}`);
};

const parseObjectSection = (
  node: ts.ObjectLiteralExpression,
  section: SlotKind,
  shared: Map<string, SharedValue>,
  controllersByName: Map<string, PidControllerDef>,
): SectionEntry[] => {
  const entries: SectionEntry[] = [];
  const pushEntry = (key: string, value: FieldValue, pid?: PidControllerDef): void => {
    entries.push({ key, value, pid });
  };

  for (const prop of node.properties) {
    if (ts.isSpreadAssignment(prop)) {
      const text = prop.expression.getText();
      const sharedValue = shared.get(text);
      if (sharedValue?.kind === "object") {
        for (const [key, value] of Object.entries(sharedValue.entries)) {
          pushEntry(key, value);
        }
      }
      continue;
    }
    if (ts.isShorthandPropertyAssignment(prop)) {
      const key = prop.name.text;
      const resolved = resolveIdentifier(key, section, shared, controllersByName);
      if (resolved.objectEntries) {
        for (const [subKey, value] of Object.entries(resolved.objectEntries)) {
          pushEntry(subKey, value);
        }
      } else {
        pushEntry(key, resolved.value as FieldValue, resolved.pid);
      }
      continue;
    }
    if (ts.isPropertyAssignment(prop)) {
      const key = propName(prop.name);
      if (!key) continue;
      const resolved = resolveExpression(prop.initializer, section, shared, controllersByName);
      if (resolved.objectEntries) {
        for (const [subKey, value] of Object.entries(resolved.objectEntries)) {
          pushEntry(subKey, value);
        }
      } else {
        pushEntry(key, resolved.value as FieldValue, resolved.pid);
      }
      continue;
    }
    if (ts.isMethodDeclaration(prop) || ts.isGetAccessorDeclaration(prop)) {
      const key = propName(prop.name);
      if (!key) continue;
      const ret = firstReturnExpr(prop.body);
      if (!ret) continue;
      const ref = instanceKeyFromChain(ret);
      if (ref !== "") pushEntry(key, { kind: "ref", ref });
    }
  }
  return entries;
};

const friendlyTitle = (module: string, field: string): string => {
  const stripped = field.startsWith(module) ? field.slice(module.length) : field;
  const camel = stripped.charAt(0).toLowerCase() + stripped.slice(1);
  return camel
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2")
    .replace(/^./, (c) => c.toUpperCase());
};

export const parseInstanceFile = (
  filePath: string,
  module: string,
  folder: string,
  key: string,
  shared: Map<string, SharedValue>,
  controllersByName: Map<string, PidControllerDef>,
  folderTooltip?: TooltipInfo,
): InstanceModel => {
  const source = createSource(filePath);
  let componentType = "";
  let objectLiteral: ts.ObjectLiteralExpression | undefined;
  const visitNode = (n: ts.Node): void => {
    if (componentType && objectLiteral) return;
    if (
      ts.isCallExpression(n) &&
      ts.isIdentifier(n.expression) &&
      n.expression.text === "toInstance"
    ) {
      const typeArg = n.typeArguments?.[0];
      if (typeArg && ts.isTypeReferenceNode(typeArg) && ts.isQualifiedName(typeArg.typeName)) {
        componentType = typeArg.typeName.right.text;
      }
      const arg = n.arguments[0];
      if (arg && ts.isObjectLiteralExpression(arg)) objectLiteral = arg;
      return;
    }
    ts.forEachChild(n, visitNode);
  };
  visitNode(source);
  if (!componentType || !objectLiteral) {
    throw new Error(`Could not parse instance file: ${filePath}`);
  }

  const slots: SlotValue[] = [];
  let inlineTooltip: TooltipInfo | undefined;

  for (const prop of objectLiteral.properties) {
    if (
      (ts.isMethodDeclaration(prop) || ts.isGetAccessorDeclaration(prop)) &&
      prop.name.getText() === "tooltip"
    ) {
      const ret = firstReturnExpr(prop.body);
      if (
        ret &&
        ts.isCallExpression(ret) &&
        ts.isIdentifier(ret.expression) &&
        ret.expression.text === "fieldTooltip"
      ) {
        inlineTooltip = parseTooltipObject(ret);
      }
      continue;
    }
    if (!ts.isPropertyAssignment(prop)) continue;
    const section = propName(prop.name);
    if (!section) continue;
    const initializer = prop.initializer;

    if (section === "source") {
      const resolved = resolveExpression(initializer, "source", shared, controllersByName);
      if (resolved.objectEntries) continue;
      slots.push({ slotId: "source", kind: "source", value: resolved.value as FieldValue });
      continue;
    }

    const slotKind: SlotKind = section as SlotKind;
    if (initializer && ts.isObjectLiteralExpression(initializer)) {
      const entries = parseObjectSection(initializer, slotKind, shared, controllersByName);
      for (const entry of entries) {
        slots.push({
          slotId: `${section}.${entry.key}`,
          kind: slotKind,
          value: entry.value,
          pid: entry.pid,
        });
      }
    } else if (ts.isIdentifier(initializer)) {
      const resolved = resolveIdentifier(initializer.text, slotKind, shared, controllersByName);
      if (resolved.objectEntries) {
        for (const [subKey, value] of Object.entries(resolved.objectEntries)) {
          slots.push({ slotId: `${section}.${subKey}`, kind: slotKind, value, pid: resolved.pid });
        }
      } else {
        slots.push({
          slotId: section,
          kind: slotKind,
          value: resolved.value as FieldValue,
          pid: resolved.pid,
        });
      }
    } else {
      const resolved = resolveExpression(initializer, slotKind, shared, controllersByName);
      if (resolved.objectEntries) continue;
      slots.push({
        slotId: section,
        kind: slotKind,
        value: resolved.value as FieldValue,
        pid: resolved.pid,
      });
    }
  }

  const sourceSlot = slots.find((s) => s.slotId === "source");
  const title =
    sourceSlot?.value.kind === "custom" && sourceSlot.value.title
      ? sourceSlot.value.title
      : sourceSlot?.value.kind === "field"
        ? friendlyTitle(module, sourceSlot.value.field)
        : "";

  return {
    module,
    folder,
    key,
    componentType,
    title,
    tooltip: inlineTooltip ?? folderTooltip,
    slots,
  };
};

export const parseModuleData = (moduleDir: string, module: string): ModuleData => {
  const dataDir = path.join(moduleDir, "data");
  const controllers = parseControllersTs(path.join(dataDir, "controllers", "index.ts"));
  const controllersByName = new Map(controllers.map((c) => [c.name, c]));
  const instances: InstanceModel[] = [];

  const folderDirs = readdirSync(dataDir, { withFileTypes: true })
    .filter((d) => d.isDirectory() && d.name !== "controllers")
    .map((d) => d.name);

  for (const folder of folderDirs) {
    const folderDir = path.join(dataDir, folder);
    const indexPath = path.join(folderDir, "index.ts");
    if (!existsSync(indexPath)) continue;
    const shared = parseSharedTs(path.join(folderDir, "shared.ts"));
    const folderTooltip = [...shared.values()].find((v) => v.kind === "tooltip")?.tooltip;
    const index = parseFolderIndex(indexPath);
    const files = readdirSync(folderDir).filter((f) => f.startsWith("_") && f.endsWith(".ts"));
    if (files.length === 0 && Object.keys(index.componentKeys).length > 0) {
      instances.push(...parseFactoryInstances(indexPath, module, folder, folderTooltip));
      continue;
    }
    for (const file of files) {
      const key = index.filenameToKey[file.replace(/\.ts$/, "")];
      if (!key) continue;
      const instance = parseInstanceFile(
        path.join(folderDir, file),
        module,
        folder,
        key,
        shared,
        controllersByName,
        folderTooltip,
      );
      instances.push(instance);
    }
  }

  return { module, instances, controllers };
};

const assembleString = (
  node: ts.Expression | undefined,
  paramName: string,
  id: string,
): string | undefined => {
  if (!node) return undefined;
  if (ts.isStringLiteral(node)) return node.text;
  if (ts.isNoSubstitutionTemplateLiteral(node)) return node.text;
  if (ts.isIdentifier(node)) return node.text === paramName ? id : undefined;
  if (ts.isTemplateExpression(node)) {
    let out = node.head.text;
    for (const span of node.templateSpans) {
      out += span.expression.getText() === paramName ? id : span.expression.getText();
      out += span.literal.text;
    }
    return out;
  }
  return undefined;
};

const parseFactoryCustom = (call: ts.CallExpression, paramName: string, id: string): FieldValue => {
  const value: Extract<FieldValue, { kind: "custom" }> = {
    kind: "custom",
    module: stringArg(call, 0),
    technicalName: "",
  };
  const obj = call.arguments[1];
  if (obj && ts.isObjectLiteralExpression(obj)) {
    for (const prop of obj.properties) {
      if (!ts.isPropertyAssignment(prop)) continue;
      const key = propName(prop.name);
      if (!key) continue;
      const text = assembleString(prop.initializer, paramName, id);
      if (text === undefined) continue;
      if (key === "title") value.title = text;
      if (key === "yardTag") value.yardTag = text;
      if (key === "technicalName") value.technicalName = text;
    }
  }
  return value;
};

export const parseFactoryInstances = (
  indexPath: string,
  module: string,
  folder: string,
  folderTooltip?: TooltipInfo,
): InstanceModel[] => {
  const source = createSource(indexPath);
  let ids: string[] = [];
  for (const statement of source.statements) {
    if (!ts.isVariableStatement(statement)) continue;
    for (const decl of statement.declarationList.declarations) {
      if (
        ts.isIdentifier(decl.name) &&
        decl.initializer &&
        ts.isArrayLiteralExpression(decl.initializer)
      ) {
        ids = decl.initializer.elements.filter(ts.isStringLiteral).map((e) => e.text);
      }
    }
  }

  let paramName = "";
  let toInstanceObj: ts.ObjectLiteralExpression | undefined;
  let componentType = "";
  const indexTooltip = parseTooltipObject(source) ?? folderTooltip;
  const visitNode = (n: ts.Node): void => {
    if (ts.isArrowFunction(n)) {
      const firstParam = n.parameters[0];
      const candidateParam =
        firstParam && ts.isIdentifier(firstParam.name) ? firstParam.name.text : "";
      const visitBody = (b: ts.Node): void => {
        if (
          ts.isCallExpression(b) &&
          ts.isIdentifier(b.expression) &&
          b.expression.text === "toInstance"
        ) {
          if (!toInstanceObj) {
            paramName = candidateParam;
            const typeArg = b.typeArguments?.[0];
            if (
              typeArg &&
              ts.isTypeReferenceNode(typeArg) &&
              ts.isQualifiedName(typeArg.typeName)
            ) {
              componentType = typeArg.typeName.right.text;
            }
            const arg = b.arguments[0];
            if (arg && ts.isObjectLiteralExpression(arg)) toInstanceObj = arg;
          }
          return;
        }
        ts.forEachChild(b, visitBody);
      };
      visitBody(n.body);
    }
    ts.forEachChild(n, visitNode);
  };
  visitNode(source);
  if (!toInstanceObj || !componentType) return [];
  const instanceObject = toInstanceObj;

  return ids.map((id) => {
    const slots: SlotValue[] = [];
    for (const prop of instanceObject.properties) {
      if (!ts.isPropertyAssignment(prop)) continue;
      const section = propName(prop.name);
      if (section === "source" && isGetCustomField(prop.initializer)) {
        slots.push({
          slotId: "source",
          kind: "source",
          value: parseFactoryCustom(prop.initializer, paramName, id),
        });
      }
    }
    return {
      module,
      folder,
      key: id,
      componentType,
      title: "",
      tooltip: indexTooltip,
      slots,
    };
  });
};
