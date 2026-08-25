export type FieldKind = "field" | "custom" | "literal" | "enum" | "ref";

export type FieldValue =
  | { kind: "field"; fieldType: string; module: string; field: string }
  | { kind: "custom"; module: string; title?: string; yardTag?: string; technicalName: string }
  | { kind: "literal"; value: string }
  | { kind: "enum"; enumName: string; member: string }
  | { kind: "ref"; ref: string };

export type SlotKind = "source" | "sensor" | "control" | "parameter" | "controllerState" | "custom";

export interface PidControllerDef {
  name: string;
  pidType: "temperature" | "flow";
  controllerField: Extract<FieldValue, { kind: "field" }>;
  setpoint?: Extract<FieldValue, { kind: "field" }>;
  outputMinimum?: Extract<FieldValue, { kind: "field" }>;
}

export interface SlotValue {
  slotId: string;
  kind: SlotKind;
  value: FieldValue;
  pid?: PidControllerDef;
}

export interface TooltipInfo {
  title?: string;
  componentType?: string;
  technicalName?: string;
}

export interface InstanceModel {
  module: string;
  folder: string;
  key: string;
  componentType: string;
  title: string;
  tooltip?: TooltipInfo;
  slots: SlotValue[];
}

export interface ModuleData {
  module: string;
  instances: InstanceModel[];
  controllers: PidControllerDef[];
}

export interface SchemaRow {
  module: string;
  section: "sensorValues" | "controlValues" | "parameters" | "controllerState";
  field: string;
  componentType: string;
  valveType?: string;
  yardTag: string;
  technicalName: string;
  friendlyName: string;
}

export interface TemplateSlot {
  componentType: string;
  slotId: string;
  slotLabel: string;
  kind: SlotKind;
  valueKinds: FieldKind[];
  allowedFieldTypes: string[];
  required: boolean;
  tooltipTitle: string;
  tooltipComponentType: string;
}
