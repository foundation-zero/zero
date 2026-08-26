import { SheetValueKind, SlotKind, TemplateSlot } from "./types";

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

export const TYPE_LABELS: Record<string, string> = {
  BoilerTank: "Boiler tank",
  CheckValve: "Check valve",
  ExchangeCircuit: "Exchange circuit",
  FlowControlValve: "Flow control valve",
  FreshwaterCircuit: "Connecting circuit",
  HeatExchanger: "Heat exchanger",
  HeatPump: "Heat pump",
  HVAC: "HVAC",
  LevelSensor: "Level sensor",
  LevelSwitch: "Level switch",
  ManualPump: "Manual pump",
  ManualValve: "Manual valve",
  MixValve: "Mix valve",
  PressureGauge: "Pressure gauge",
  PressureSensor: "Pressure sensor",
  Pump: "Pump",
  SwitchValve: "Switch valve",
  TemperatureSensor: "Temperature sensor",
  ThreeWaySwitchValve: "Three-way switch valve",
};

export const typeLabelOf = (componentType: string): string =>
  TYPE_LABELS[componentType] ?? componentType;

export interface CanonicalSlot {
  slotId: string;
  kind: SlotKind;
  valueKind: SheetValueKind;
  fieldTypes?: string[];
  required: boolean;
}

const field = (
  slotId: string,
  kind: SlotKind,
  fieldTypes: string[],
  required = true,
): CanonicalSlot => ({ slotId, kind, valueKind: "field", fieldTypes, required });
const customSource = (): CanonicalSlot => ({
  slotId: "source",
  kind: "source",
  valueKind: "customSource",
  required: true,
});

export const CANONICAL_SLOTS: Record<string, CanonicalSlot[]> = {
  BoilerTank: [
    customSource(),
    field("sensors.level", "sensor", ["sensor:level"]),
    field("sensors.temperature", "sensor", ["sensor:temperature"]),
    field("sensors.boostingSupply", "sensor", ["sensor:temperature"]),
    field("sensors.boostSupplyValve", "sensor", ["sensor:valve"]),
    field("sensors.boostReturnValve", "sensor", ["sensor:valve"]),
    field("sensors.supplyValve", "sensor", ["sensor:valve"]),
    field("sensors.dischargeValve", "sensor", ["sensor:valve"]),
    field("parameters.minimumLevel", "parameter", ["parameter:level"]),
    field("parameters.maximumLevel", "parameter", ["parameter:level"]),
    field("parameters.minimumTemperature", "parameter", ["parameter:temperature"]),
    field("parameters.maximumTemperature", "parameter", ["parameter:temperature"]),
    field("parameters.enabled", "parameter", ["parameter:enabled"]),
    field("controllerState.controller", "controllerState", ["controller:dhwTanksController"]),
    { slotId: "custom.tankStateField", kind: "custom", valueKind: "literal", required: true },
  ],
  ExchangeCircuit: [
    customSource(),
    field("sensors.incoming", "sensor", ["sensor:temperature"]),
    field("sensors.outgoing", "sensor", ["sensor:temperature"]),
    field("sensors.flow", "sensor", ["sensor:flow"]),
    field("sensors.deltaT", "sensor", ["sensor:deltaT"]),
    field("sensors.heatExchanger", "sensor", ["sensor:heatExchanger"]),
    { slotId: "custom.circuitName", kind: "custom", valueKind: "literal", required: true },
  ],
  FreshwaterCircuit: [
    customSource(),
    field("sensors.flowIn", "sensor", ["sensor:flow", "sensor:calculatedFlow"]),
    field("sensors.flowOut", "sensor", ["sensor:flow", "sensor:calculatedFlow"]),
    field("sensors.tIn", "sensor", ["sensor:temperature"]),
    field("sensors.tOut", "sensor", ["sensor:temperature"]),
  ],
  HeatPump: [
    field("source", "source", ["sensor:heatExchanger"]),
    field("sensors.incoming", "sensor", ["sensor:temperature"]),
    field("sensors.outgoing", "sensor", ["sensor:temperature"]),
    field("controls.heatpump", "control", ["control:heatpump"]),
    {
      slotId: "custom.controller",
      kind: "custom",
      valueKind: "controllerRef",
      required: false,
    },
  ],
  Pump: [
    field("source", "source", ["sensor:pump"]),
    field("controls.pump", "control", ["control:pump"]),
    { slotId: "custom.flowController", kind: "custom", valueKind: "controllerRef", required: true },
    {
      slotId: "custom.temperatureController",
      kind: "custom",
      valueKind: "controllerRef",
      required: false,
    },
    field("parameters.flow", "parameter", ["parameter:flow"], false),
    field("parameters.temperature", "parameter", ["parameter:temperature"], false),
  ],
  HVAC: [
    field("source", "source", ["sensor:heatExchanger"]),
    field("sensors.incoming", "sensor", ["sensor:temperature"]),
    field("sensors.outgoing", "sensor", ["sensor:temperature"]),
    field("sensors.flow", "sensor", ["sensor:flow"]),
  ],
  HeatExchanger: [
    field("source", "source", ["sensor:heatExchanger"]),
    field("sensors.incoming", "sensor", ["sensor:temperature"]),
    field("sensors.outgoing", "sensor", ["sensor:temperature"]),
    field("sensors.flow", "sensor", ["sensor:flow"]),
    { slotId: "custom.sideA", kind: "custom", valueKind: "enum", required: true },
    { slotId: "custom.sideB", kind: "custom", valueKind: "enum", required: true },
    {
      slotId: "custom.exchangeCircuit",
      kind: "custom",
      valueKind: "instanceRef",
      required: true,
    },
  ],
  SwitchValve: [
    field("source", "source", ["sensor:valve"]),
    field("controls.valve", "control", ["control:valve"]),
    {
      slotId: "custom.tankController",
      kind: "custom",
      valueKind: "instanceRef",
      required: false,
    },
  ],
  FlowControlValve: [
    field("source", "source", ["sensor:valve"]),
    field("controls.valve", "control", ["control:valve"]),
    field("sensors.measurement", "sensor", ["sensor:flow"], false),
    field("parameters.flow", "parameter", ["parameter:tuning", "parameter:flow"], false),
    field("controllerState.controller", "controllerState", ["pidController"], false),
    {
      slotId: "custom.controller",
      kind: "custom",
      valueKind: "controllerRef",
      required: false,
    },
  ],
  MixValve: [
    field("source", "source", ["sensor:valve"]),
    field("controls.valve", "control", ["control:valve"]),
    field("controllerState.controller", "controllerState", ["pidController"], false),
  ],
  ThreeWaySwitchValve: [
    field("source", "source", ["sensor:valve"]),
    field("controls.valve", "control", ["control:valve"]),
  ],
  ManualValve: [customSource()],
  CheckValve: [customSource()],
  ManualPump: [customSource()],
  PressureGauge: [customSource()],
  TemperatureSensor: [
    field("source", "source", ["sensor:temperature"]),
    {
      slotId: "custom.controller",
      kind: "custom",
      valueKind: "controllerRef",
      required: false,
    },
    field("controllerState.controller", "controllerState", ["pidController"], false),
    field("controls.pump", "control", ["control:pump"], false),
    field("parameters.temperature", "parameter", ["parameter:temperature"], false),
    field("sensors.measurement", "sensor", ["sensor:flow", "sensor:temperature"], false),
    field("sensors.actuator", "sensor", ["sensor:valve"], false),
  ],
  PressureSensor: [
    field("source", "source", ["sensor:pressure"]),
    {
      slotId: "custom.controller",
      kind: "custom",
      valueKind: "controllerRef",
      required: false,
    },
    field("controls.pump", "control", ["control:pump"], false),
    field("parameters.flow", "parameter", ["parameter:flowcontrol", "parameter:flow"], false),
    field("sensors.flow", "sensor", ["sensor:flow"], false),
  ],
  FlowSensor: [
    field("source", "source", ["sensor:flow"]),
    {
      slotId: "custom.controller",
      kind: "custom",
      valueKind: "controllerRef",
      required: false,
    },
    field("controllerState.controller", "controllerState", ["pidController"], false),
    field("controls.pump", "control", ["control:pump"], false),
    field("parameters.flow", "parameter", ["parameter:flowcontrol", "parameter:flow"], false),
    field("sensors.temperature", "sensor", ["sensor:temperature"], false),
    field("sensors.measurement", "sensor", ["sensor:flow", "sensor:temperature"], false),
  ],
  LevelSensor: [field("source", "source", ["sensor:level"])],
  LevelSwitch: [field("source", "source", ["sensor:levelSwitch"])],
};

export const canonicalSlotsOf = (componentType: string): CanonicalSlot[] =>
  CANONICAL_SLOTS[componentType] ?? [];

export const templateRows = (): TemplateSlot[] =>
  Object.entries(CANONICAL_SLOTS)
    .flatMap(([componentType, slots]) =>
      slots.map((slot) => ({
        componentType,
        typeLabel: typeLabelOf(componentType),
        slotId: slot.slotId,
        slotLabel: slotLabel(slot.slotId),
        kind: slot.kind,
        valueKind: slot.valueKind,
        allowedFieldTypes: slot.fieldTypes ?? [],
        required: slot.required,
      })),
    )
    .sort((a, b) =>
      a.componentType === b.componentType
        ? a.slotId.localeCompare(b.slotId)
        : a.componentType.localeCompare(b.componentType),
    );

export const templateHeaders = [
  "componentType",
  "typeLabel",
  "slotId",
  "slotLabel",
  "kind",
  "valueKind",
  "allowedFieldTypes",
  "required",
];

export const toTemplateRow = (template: TemplateSlot): Record<string, string> => ({
  componentType: template.componentType,
  typeLabel: template.typeLabel,
  slotId: template.slotId,
  slotLabel: template.slotLabel,
  kind: template.kind,
  valueKind: template.valueKind,
  allowedFieldTypes: template.allowedFieldTypes.join(";"),
  required: String(template.required),
});
