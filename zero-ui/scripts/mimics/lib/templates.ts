import { InstanceModel, ModuleData, SlotKind, TemplateSlot } from "./types";

const SECTION_LABELS: Record<SlotKind, string> = {
  source: "Source",
  sensor: "Sensor",
  control: "Control",
  parameter: "Parameter",
  controllerState: "Controller",
  custom: "Custom",
};

export const slotLabel = (slotId: string): string => {
  const dot = slotId.indexOf(".");
  if (dot === -1) return SECTION_LABELS[slotId as SlotKind] ?? slotId;
  const section = slotId.slice(0, dot) as SlotKind;
  const key = slotId.slice(dot + 1);
  return `${SECTION_LABELS[section] ?? section} › ${key}`;
};

export const deriveTemplates = (modules: ModuleData[]): TemplateSlot[] => {
  const byType = new Map<string, InstanceModel[]>();
  for (const module of modules) {
    for (const instance of module.instances) {
      const list = byType.get(instance.componentType) ?? [];
      list.push(instance);
      byType.set(instance.componentType, list);
    }
  }

  const templates: TemplateSlot[] = [];
  for (const [componentType, instances] of byType) {
    const slotIds = new Set<string>();
    for (const instance of instances) {
      for (const slot of instance.slots) slotIds.add(slot.slotId);
    }

    const tooltips = instances.map((i) => i.tooltip);
    const tooltipTitle = tooltips.every((t) => t?.title === tooltips[0]?.title)
      ? (tooltips[0]?.title ?? "")
      : "";
    const tooltipComponentType = tooltips.every(
      (t) => t?.componentType === tooltips[0]?.componentType,
    )
      ? (tooltips[0]?.componentType ?? "")
      : "";

    for (const slotId of [...slotIds].sort()) {
      const slotInstances = instances.filter((i) => i.slots.some((s) => s.slotId === slotId));
      const kind = slotInstances[0]?.slots.find((s) => s.slotId === slotId)?.kind ?? "custom";
      const valueKinds = new Set(
        slotInstances.flatMap((i) =>
          i.slots.filter((s) => s.slotId === slotId).map((s) => s.value.kind),
        ),
      );
      const fieldTypes = new Set<string>();
      for (const instance of slotInstances) {
        for (const s of instance.slots) {
          if (s.slotId === slotId && s.value.kind === "field") fieldTypes.add(s.value.fieldType);
        }
      }
      templates.push({
        componentType,
        slotId,
        slotLabel: slotLabel(slotId),
        kind,
        valueKinds: [...valueKinds],
        allowedFieldTypes: [...fieldTypes].sort(),
        required: slotInstances.length === instances.length,
        tooltipTitle,
        tooltipComponentType,
      });
    }
  }

  return templates.sort((a, b) =>
    a.componentType === b.componentType
      ? a.slotId.localeCompare(b.slotId)
      : a.componentType.localeCompare(b.componentType),
  );
};

export const templateHeaders = [
  "componentType",
  "slotId",
  "slotLabel",
  "kind",
  "valueKind",
  "allowedFieldTypes",
  "required",
  "tooltipTitle",
  "tooltipComponentType",
];

export const toTemplateRow = (template: TemplateSlot): Record<string, string> => ({
  componentType: template.componentType,
  slotId: template.slotId,
  slotLabel: template.slotLabel,
  kind: template.kind,
  valueKind: template.valueKinds.join(";"),
  allowedFieldTypes: template.allowedFieldTypes.join(";"),
  required: String(template.required),
  tooltipTitle: template.tooltipTitle,
  tooltipComponentType: template.tooltipComponentType,
});
