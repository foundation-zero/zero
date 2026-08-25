import { slotLabel } from "./templates";
import { InstanceModel, SlotValue } from "./types";

export const instancesHeaders = [
  "module",
  "folder",
  "key",
  "componentType",
  "title",
  "tooltipTitle",
  "tooltipComponentType",
  "tooltipTechnicalName",
  "slots",
];

export const toInstancesRow = (instance: InstanceModel): Record<string, string> => ({
  module: instance.module,
  folder: instance.folder,
  key: instance.key,
  componentType: instance.componentType,
  title: instance.title,
  tooltipTitle: instance.tooltip?.title ?? "",
  tooltipComponentType: instance.tooltip?.componentType ?? "",
  tooltipTechnicalName: instance.tooltip?.technicalName ?? "",
  slots: instance.slots.map((s) => s.slotId).join(";"),
});

export const fillInHeaders = [
  "module",
  "folder",
  "instanceKey",
  "componentType",
  "title",
  "tooltipTitle",
  "tooltipComponentType",
  "tooltipTechnicalName",
  "slotId",
  "slotLabel",
  "kind",
  "valueKind",
  "fieldType",
  "fieldName",
  "sourceModule",
  "customTitle",
  "customYardTag",
  "customTechnicalName",
  "literalValue",
  "refTarget",
  "pidType",
  "pidControllerField",
  "pidSetpointField",
  "pidOutputMinimumField",
  "notes",
];

const toFillInRow = (instance: InstanceModel, slot: SlotValue): Record<string, string> => {
  const row: Record<string, string> = {
    module: instance.module,
    folder: instance.folder,
    instanceKey: instance.key,
    componentType: instance.componentType,
    title: instance.title,
    tooltipTitle: instance.tooltip?.title ?? "",
    tooltipComponentType: instance.tooltip?.componentType ?? "",
    tooltipTechnicalName: instance.tooltip?.technicalName ?? "",
    slotId: slot.slotId,
    slotLabel: slotLabel(slot.slotId),
    kind: slot.kind,
    valueKind: slot.value.kind,
    fieldType: "",
    fieldName: "",
    sourceModule: "",
    customTitle: "",
    customYardTag: "",
    customTechnicalName: "",
    literalValue: "",
    refTarget: "",
    pidType: "",
    pidControllerField: "",
    pidSetpointField: "",
    pidOutputMinimumField: "",
    notes: "",
  };

  switch (slot.value.kind) {
    case "field":
      row.sourceModule = slot.value.module;
      row.fieldType = slot.value.fieldType;
      row.fieldName = slot.value.field;
      break;
    case "custom":
      row.sourceModule = slot.value.module;
      row.customTitle = slot.value.title ?? "";
      row.customYardTag = slot.value.yardTag ?? "";
      row.customTechnicalName = slot.value.technicalName;
      break;
    case "literal":
      row.literalValue = slot.value.value;
      break;
    case "enum":
      row.refTarget = `enum:${slot.value.enumName}.${slot.value.member}`;
      break;
    case "ref":
      row.refTarget = slot.value.ref;
      break;
  }

  if (slot.pid) {
    row.pidType = slot.pid.pidType;
    row.pidControllerField = slot.pid.controllerField.field;
    row.pidSetpointField = slot.pid.setpoint?.field ?? "";
    row.pidOutputMinimumField = slot.pid.outputMinimum?.field ?? "";
  }

  return row;
};

export const instancesToFillIn = (instances: InstanceModel[]): Record<string, string>[] => {
  const rows: Record<string, string>[] = [];
  for (const instance of instances) {
    const sorted = [...instance.slots].sort((a, b) => a.slotId.localeCompare(b.slotId));
    for (const slot of sorted) {
      rows.push(toFillInRow(instance, slot));
    }
  }
  return rows;
};
