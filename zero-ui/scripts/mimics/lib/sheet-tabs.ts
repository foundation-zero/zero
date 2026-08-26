import { canonicalSlotsOf, slotLabel, typeLabelOf } from "./templates";
import { InstanceModel, ModuleData, PidControllerDef, SlotValue } from "./types";

export const instanceHeaders = ["module", "folder", "key", "title", "componentType"];

export const toInstancesRow = (instance: InstanceModel): Record<string, string> => ({
  module: instance.module,
  folder: instance.folder,
  key: instance.key,
  title: instance.title,
  componentType: instance.componentType,
});

export const planHeaders = [
  "module",
  "folder",
  "key",
  "title",
  "componentType",
  "typeLabel",
  "slotId",
  "slotLabel",
  "kind",
  "valueKind",
  "allowedFieldTypes",
  "required",
  "value",
  "srcTitle",
  "srcYardTag",
  "notes",
];

interface SerializedValue {
  value: string;
  srcTitle: string;
  srcYardTag: string;
}

const serializeSlot = (
  slot: SlotValue,
  instanceModule: string,
  fieldModules: Map<string, Set<string>>,
): SerializedValue => {
  switch (slot.value.kind) {
    case "field": {
      const modules = fieldModules.get(slot.value.field);
      const needsQualifier = !modules || modules.size > 1 || !modules.has(instanceModule);
      return {
        value: needsQualifier ? `${slot.value.module}:${slot.value.field}` : slot.value.field,
        srcTitle: "",
        srcYardTag: "",
      };
    }
    case "custom":
      return {
        value: slot.value.technicalName,
        srcTitle: slot.value.title ?? "",
        srcYardTag: slot.value.yardTag ?? "",
      };
    case "literal":
      return { value: slot.value.value, srcTitle: "", srcYardTag: "" };
    case "enum":
      return { value: slot.value.member, srcTitle: "", srcYardTag: "" };
    case "ref":
      return {
        value: `${slot.pid ? "@controller:" : "@instance:"}${slot.value.ref}`,
        srcTitle: "",
        srcYardTag: "",
      };
  }
};

const VALUE_KIND_BY_FIELD_KIND: Record<SlotValue["kind"], string> = {
  field: "field",
  custom: "customSource",
  literal: "literal",
  enum: "enum",
  ref: "instanceRef",
};

const toPlanRow = (
  instance: InstanceModel,
  slotId: string,
  value: SlotValue | undefined,
  required: boolean,
  allowedFieldTypes: string[],
  fieldModules: Map<string, Set<string>>,
): Record<string, string> => {
  const serialized = value
    ? serializeSlot(value, instance.module, fieldModules)
    : { value: "", srcTitle: "", srcYardTag: "" };
  return {
    module: instance.module,
    folder: instance.folder,
    key: instance.key,
    title: instance.title,
    componentType: instance.componentType,
    typeLabel: typeLabelOf(instance.componentType),
    slotId,
    slotLabel: slotLabel(slotId),
    kind: value?.kind ?? (slotId.split(".")[0] as SlotValue["kind"]),
    valueKind: value ? (value.pid ? "controllerRef" : VALUE_KIND_BY_FIELD_KIND[value.kind]) : "",
    allowedFieldTypes: allowedFieldTypes.join(";"),
    required: String(required),
    value: serialized.value,
    srcTitle: serialized.srcTitle,
    srcYardTag: serialized.srcYardTag,
    notes: "",
  };
};

const SLOT_ORDER = ["source", "sensors", "controls", "parameters", "controllerState", "custom"];

const bySlotOrder = (a: string, b: string): number => {
  const sectionA = a.split(".")[0];
  const sectionB = b.split(".")[0];
  const diff = SLOT_ORDER.indexOf(sectionA) - SLOT_ORDER.indexOf(sectionB);
  return diff !== 0 ? diff : a.localeCompare(b);
};

export const instancesToPlanRows = (
  instances: InstanceModel[],
  fieldModules: Map<string, Set<string>>,
): Record<string, string>[] => {
  const rows: Record<string, string>[] = [];
  for (const instance of instances) {
    const slots = new Map(instance.slots.map((slot) => [slot.slotId, slot]));
    const templateSlots = canonicalSlotsOf(instance.componentType);
    const known = new Set(templateSlots.map((template) => template.slotId));
    for (const template of templateSlots) {
      rows.push(
        toPlanRow(
          instance,
          template.slotId,
          slots.get(template.slotId),
          template.required,
          template.fieldTypes ?? [],
          fieldModules,
        ),
      );
    }
    for (const slot of [...slots.keys()].filter((slotId) => !known.has(slotId)).sort(bySlotOrder)) {
      const value = slots.get(slot);
      rows.push(
        toPlanRow(
          instance,
          slot,
          value,
          false,
          value?.kind === "field" ? [value.fieldType] : [],
          fieldModules,
        ),
      );
    }
  }
  return rows;
};

export const controllerHeaders = [
  "module",
  "name",
  "pidType",
  "controllerField",
  "setpointField",
  "outputMinimumField",
];

export const toControllersRows = (modules: ModuleData[]): Record<string, string>[] =>
  modules.flatMap((module) =>
    module.controllers.map((controller: PidControllerDef) => ({
      module: module.module,
      name: controller.name,
      pidType: controller.pidType,
      controllerField: controller.controllerField.field,
      setpointField: controller.setpoint?.field ?? "",
      outputMinimumField: controller.outputMinimum?.field ?? "",
    })),
  );
