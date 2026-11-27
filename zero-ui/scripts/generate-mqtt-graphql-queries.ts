#!/usr/bin/env node

/**
 * Generates thrapp's component definitions and its query fragments for the MQTT GraphQL API
 * (zero-mqtt-graphql) from the AsyncAPI Specs that API serves.
 *
 * A component is identified by its technical name, the last segment of its topic: the same
 * name in the IO list, the marpower Spec and thrs-control. A module shows the devices zero-data
 * puts in it (THRS, fresh water, seawater, propulsion drives, converters, …), the values
 * thrs-control computes for it (`thrs/controller/<module>/…`), and the actuators and parameters
 * thrs-control takes for it.
 *
 * Each query fragment selects a module part, each component where the API answers it, and each
 * definition carries that path, so thrapp finds its components in the response. Aliases rename
 * raw AMCS leaves and `timeStamp` to what thrapp calls them.
 *
 * It first regenerates the Specs (uncommitted) unless `--skip-specs` is given.
 *
 * Usage: pnpm generate-mqtt-graphql-queries [--skip-specs]
 */

// lodash is CommonJS: Node gives it no named exports, unlike Vite in the app.
import lodash from "lodash";
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import * as Thrs from "../src/modules/thrapp/types/thrs.ts";

const ZERO_UI = path.resolve(import.meta.dirname, "..");
const REPO = path.resolve(ZERO_UI, "..");
const SPECS = path.join(REPO, "specs");
const DEFINITIONS_OUTPUT = path.join(ZERO_UI, "src/modules/thrapp/lib/definitions.generated.ts");
const QUERIES_OUTPUT = path.join(
  ZERO_UI,
  "src/modules/thrapp/lib/mqtt-graphql-queries.generated.ts",
);

const DEVICE_PREFIX = "marpower/";
const CONTROLLER_PREFIX = "thrs/controller/";
/** zero-data's system of THRS's own modules, which keep their bare names. */
const THRS_SYSTEM = "thrs";

/**
 * The devices thrapp shows, by zero-data's system and module (`true`: every module). THRS's own,
 * the fresh water and seawater sensors its circuits connect to, and the drives and converters it
 * cools.
 */
const SHOWN: Record<string, true | string[]> = {
  [THRS_SYSTEM]: true,
  fresh_water: ["hot"],
  sea_water: ["cold"],
  propulsion: ["drive"],
  dc_700v: ["shore-converter"],
  dc_ac: ["converter"],
};

const isShown = (channelKey: string): boolean => {
  const [system, module] = channelKey.split(".");
  const modules = SHOWN[system];
  return modules === true || (modules?.includes(module) ?? false);
};

type Part = "sensorValues" | "controlValues" | "parameters" | "controllerState";

/** thrapp's component type for a Spec's `component_type`, per part. */
const SENSOR_TYPES: Record<string, keyof typeof Thrs.SensorComponentType> = {
  pump: "Pump",
  valve: "Valve",
  temperature: "Temperature",
  flow: "Flow",
  flow_only: "FlowOnly",
  pressure: "Pressure",
  level_sensor: "Level",
  level_switch: "LevelSwitch",
  pyranometer: "Pyranometer",
  amcs_mode: "AmcsMode",
  heat_transfer: "HeatTransferDevice",
  calculated_flow: "CalculatedFlow",
  calculated_temperature: "CalculatedTemperature",
  brightloop: "Brightloop",
  brightloop_group: "BrightloopGroup",
  ugrid_group: "UgridGroup",
  shore_power_group: "ShorePowerGroup",
  drive: "PropulsionDrive",
  shore_converter: "ShorePowerConverter",
  converter: "Ugrid",
  pcm: "HeatTransferDevice",
};

const CONTROLLER_STATE_TYPES: Record<string, keyof typeof Thrs.ControllerStateComponentType> = {
  pid_controller: "PIDController",
  tank_controller: "DhwTanksController",
  pcm_charge_controller: "PcmChargeController",
};

const CONTROL_TYPES: Record<string, keyof typeof Thrs.ControlComponentType> = {
  pump: "Pump",
  valve: "Valve",
  heatpump: "Heatpump",
  pcm: "Pcm",
  adsorption_chiller: "AdsorptionChiller",
};

// The fields thrapp reads per component type, as thrs-api named them.

const CONTROL_FIELDS: Record<string, string[]> = {
  Pump: ["dutypoint", "on"],
  Valve: ["setpoint"],
  Pcm: ["on"],
  Heatpump: ["temperatureSetpoint", "on"],
  AdsorptionChiller: ["enable"],
};

const CONTROLLER_STATE_FIELDS: Record<string, string[]> = {
  PIDController: ["target", "measurement", "output", "error", "enabled", "tuning", "components"],
  DhwTanksController: ["tank1State", "tank2State", "tank3State", "timeToFill", "timeToHot"],
  PcmChargeController: ["charge", "energy", "chargingState", "chargeStatus"],
};

const SENSOR_FIELDS: Record<string, string[]> = {
  Temperature: ["temperature"],
  CalculatedTemperature: ["temperature"],
  Pressure: ["pressure"],
  Flow: ["flow", "temperature", "quantity"],
  FlowOnly: ["flow"],
  Pump: [
    "flow",
    "speed",
    "opTime",
    "pressure",
    "energyConsumption",
    "powerInput",
    "anyFailureActive",
    "anyWarningActive",
    "feedbackFailure",
    "externalOutOfRange",
  ],
  Valve: [
    "positionRel",
    "positionAbs",
    "anyFailureActive",
    "anyWarningActive",
    "feedbackFailure",
    "externalOutOfRange",
  ],
  Level: ["level"],
  LevelSwitch: ["empty"],
  HeatTransferDevice: ["temperatureSupply", "temperatureReturn", "flow", "heat", "deltaT"],
  CalculatedFlow: ["flow"],
  Brightloop: ["active", "maxChannelTemperature", "power"],
  BrightloopGroup: ["anyActive", "maxChannelTemperature", "totalPower"],
  UgridGroup: ["anyActive", "maxTempPowerStage", "totalPower"],
  ShorePowerGroup: [
    "anyActive",
    "maxEsiTransformerTemperature",
    "minEsiIgbtMinTemperature",
    "maxEsiIgbtMaxTemperature",
    "totalPower",
  ],
  PropulsionDrive: ["active", "tempPowerStage", "power"],
  ShorePowerConverter: [
    "active",
    "esiTransformerTemperature",
    "esiIgbtMinTemperature",
    "esiIgbtMaxTemperature",
    "power",
  ],
  Ugrid: ["active", "tempPowerStage", "power"],
  Pyranometer: ["irradiance"],
  AmcsMode: ["mode"],
};

/** The parts whose components have fields; a parameter is a field itself. */
type ComponentPart = Exclude<Part, "parameters">;

const FIELDS_BY_PART: Record<ComponentPart, Record<string, string[]>> = {
  sensorValues: SENSOR_FIELDS,
  controlValues: CONTROL_FIELDS,
  controllerState: CONTROLLER_STATE_FIELDS,
};

/** Stamped leaves whose source (measured or estimated) thrapp shows. */
const WITH_SOURCE: Record<string, string[]> = {
  HeatTransferDevice: ["temperatureSupply", "temperatureReturn", "flow"],
};

/** The payload keys of the sensor leaves a device names differently from thrapp, per type. */
const SENSOR_KEYS: Record<string, Record<string, string>> = {
  PropulsionDrive: { active: "VpEnable" },
  ShorePowerConverter: { active: "Online", power: "EsiAcBusActivePower3Phase" },
  Ugrid: { active: "Running", power: "PvPower" },
};

// ============================================================================
// Names
// ============================================================================

/**
 * A topic segment or schema key as the MQTT GraphQL API names it (zero-mqtt-graphql's
 * `sanitize_to_graphql_name`): camelCase, digit groups kept apart by `_` (`string-1-2` →
 * `string1_2`), and a leading `_` before a digit.
 */
const graphqlName = (raw: string): string => {
  const words = raw
    .split(/[^A-Za-z0-9]+/)
    .flatMap((chunk) =>
      chunk
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/([A-Z])([A-Z][a-z])/g, "$1 $2")
        .replace(/([0-9])([A-Za-z])/g, "$1 $2")
        .split(" "),
    )
    .filter((word) => word.length > 0);
  const name = words.reduce((acc, word, index) => {
    const cased = index === 0 ? word.toLowerCase() : capitalize(word.toLowerCase());
    const separator = /[0-9]$/.test(acc) && /^[0-9]/.test(cased) ? "_" : "";
    return `${acc}${separator}${cased}`;
  }, "");
  return /^[0-9]/.test(name) ? `_${name}` : name;
};

/** `name` with its first letter in upper case (`freshWaterHot` → `FreshWaterHot`). */
const capitalize = (name: string): string => `${name.charAt(0).toUpperCase()}${name.slice(1)}`;

/** `freshWaterHot` → `FRESH_WATER_HOT`. */
const screamingSnakeCase = (name: string): string =>
  name.replace(/[A-Z]/g, (letter) => `_${letter}`).toUpperCase();

/** A name without case or separators, so names match across the Specs. */
const normalize = (name: string): string => name.toLowerCase().replace(/[^a-z0-9]/g, "");

/** An AMCS leaf name without its two-letter group prefix (`TF_AnyFailureActive` → `AnyFailureActive`). */
const unprefixed = (name: string): string => name.replace(/^[A-Z]{2}_/, "");

/**
 * The technical name of a topic: its last segment. The AMCS mode is the exception, published as
 * `<module>/mode` with the technical name `<module>-mode` (zero-data's `managed_topics.py`).
 */
const technicalName = (address: string): string => {
  const segments = address.split("/");
  return segments.at(-1) === "mode" ? `${segments.at(-2)}-mode` : segments.at(-1)!;
};

/** thrapp's valve type for marpower's `x-zero-valve-type` and thrs-control's `valve_type`. */
const VALVE_TYPES: Record<string, keyof typeof Thrs.ValveType> = {
  mix: "Mix",
  switch: "Switch",
  flowcontrol: "FlowControl",
};

const valveType = (type: unknown): keyof typeof Thrs.ValveType =>
  VALVE_TYPES[`${type}`] ?? "Unknown";

// ============================================================================
// AsyncAPI
// ============================================================================

interface Schema {
  $ref?: string;
  type?: string | string[];
  description?: string;
  properties?: Record<string, Schema>;
  anyOf?: Schema[];
  oneOf?: Schema[];
  [key: string]: unknown;
}

interface Channel {
  address: string;
  messages?: Record<string, Message>;
  "x-zero-component-type"?: string;
  "x-zero-yard-tag"?: string;
  "x-zero-valve-type"?: string;
}

interface Message {
  $ref?: string;
  payload?: Schema;
}

interface Spec {
  channels: Record<string, Channel>;
  components: { schemas: Record<string, Schema>; messages?: Record<string, Message> };
}

const readSpec = (file: string): Spec =>
  JSON.parse(fs.readFileSync(path.join(SPECS, file), "utf8"));

/** `schema` with local `$ref`s followed, and a nullable union reduced to its object arm. */
const resolve = (spec: Spec, schema: Schema | undefined): Schema | undefined => {
  if (!schema) return undefined;
  if (schema.$ref) {
    return resolve(spec, spec.components.schemas[schema.$ref.split("/").at(-1)!]);
  }
  const arms = schema.anyOf ?? schema.oneOf;
  if (arms && !schema.properties) {
    return arms.map((arm) => resolve(spec, arm)).find((arm) => arm?.properties) ?? schema;
  }
  return schema;
};

/** A channel's payload schema; its message may be inline or a `$ref` to a component message. */
const payload = (spec: Spec, channel: Channel): Schema | undefined => {
  const message = Object.values(channel.messages ?? {})[0];
  const resolved = message?.$ref
    ? spec.components.messages?.[message.$ref.split("/").at(-1)!]
    : message;
  return resolve(spec, resolved?.payload);
};

// ============================================================================
// Selections
// ============================================================================

interface Selection {
  /** The response name thrapp reads, and the API field it aliases when they differ. */
  name: string;
  field: string;
  children: Selection[];
}

/** A selection at a path of the API's tree, such as `["marpower", "_500000Thrs", "dhw"]`. */
interface PathSelection {
  path: string[];
  selection: Selection;
}

/** The leaves of a stamped value as thrapp reads them: `timeStamp` becomes `timestamp`. */
const stampedLeaves = (schema: Schema, withSource: boolean): Selection[] =>
  Object.keys(schema.properties ?? {})
    .map(graphqlName)
    .filter(
      (field) => field === "value" || field === "timeStamp" || (withSource && field === "source"),
    )
    .map((field) => ({ name: field === "timeStamp" ? "timestamp" : field, field, children: [] }));

/** The payload key holding thrapp's `leaf` of a component of `typeName`, if any. */
const payloadKey = (keys: string[], leaf: string, typeName: string): string | undefined => {
  const named = SENSOR_KEYS[typeName]?.[leaf];
  if (named) return keys.find((key) => key === named);
  return (
    keys.find((key) => normalize(key) === normalize(leaf)) ??
    keys.find((key) => normalize(unprefixed(key)) === normalize(leaf))
  );
};

// ============================================================================
// Generation
// ============================================================================

interface Component {
  key: string;
  module: string;
  topic: string;
  path: string[];
  payload: Schema | undefined;
  componentType: string;
  yardTag?: string;
  valveType?: string;
}

/** One entry of a generated definition. */
interface DefinitionEntry {
  key: string;
  /** thrapp's type, as `<Enum>.<Member>`. */
  componentType: string;
  /** Where the API answers the component, such as `["marpower", "_500000Thrs", "dhw", "dhwPump"]`. */
  path: string[];
  yardTag?: string;
  valveType?: string;
  description?: string;
}

interface ModuleOutput {
  definitions: Record<Part, DefinitionEntry[]>;
  selections: Record<Part, PathSelection[]>;
}

const emptyParts = <T>(make: () => T): Record<Part, T> => ({
  sensorValues: make(),
  controlValues: make(),
  parameters: make(),
  controllerState: make(),
});

/**
 * The components of a Spec's channels under `prefix` that `include` keeps, with the module
 * `moduleOf` gives a channel's key and address. A channel without a component type, such as a
 * subscribe-only one, is no component.
 */
const components = (
  spec: Spec,
  prefix: string,
  moduleOf: (key: string, address: string) => string,
  include: (key: string) => boolean = () => true,
): Component[] =>
  Object.entries(spec.channels).flatMap(([channelKey, channel]) => {
    const componentType = channel["x-zero-component-type"];
    const { address } = channel;
    if (!componentType || !address.startsWith(prefix) || !include(channelKey)) return [];
    return [
      {
        key: graphqlName(technicalName(address)),
        module: moduleOf(channelKey, address),
        topic: address,
        path: address.split("/").map(graphqlName),
        payload: payload(spec, channel),
        componentType,
        yardTag: channel["x-zero-yard-tag"],
        valveType: channel["x-zero-valve-type"],
      },
    ];
  });

/**
 * A device's module, from zero-data's channel key `<system>.<module>.<technical-name>`. Module
 * names repeat across systems (`cold`), so other systems' modules get the system as a prefix
 * (`freshWaterCold`); THRS's own keep their bare names.
 */
const deviceModule = (key: string): string => {
  const [system, module] = key.split(".");
  return system === THRS_SYSTEM ? module : graphqlName(`${system}_${module}`);
};

/** A computed value's module, from its address `thrs/controller/<module>/…`. */
const controllerModule = (_: string, address: string): string =>
  address.slice(CONTROLLER_PREFIX.length).split("/")[0];

/** The components of both Specs, as one generation reads them. */
interface Sources {
  marpower: Spec;
  thrsControl: Spec;
  /** The devices thrapp shows and the values thrs-control computes. */
  components: Component[];
}

/** What one module's generation reads and writes. */
interface ModuleContext {
  module: string;
  sources: Sources;
  output: ModuleOutput;
  /** What thrapp would show but the Specs give no type, field or topic for, with the reason. */
  leftOut: string[];
}

const specOf = ({ marpower, thrsControl }: Sources, component: Component): Spec =>
  component.topic.startsWith(DEVICE_PREFIX) ? marpower : thrsControl;

/** The selections of the fields thrapp reads from `component`; missing ones are left out. */
const selectFields = (
  context: ModuleContext,
  component: Component,
  part: ComponentPart,
  typeName: string,
): Selection[] => {
  const properties = component.payload?.properties ?? {};
  return (FIELDS_BY_PART[part][typeName] ?? []).flatMap((leaf): Selection[] => {
    const key = payloadKey(Object.keys(properties), leaf, typeName);
    if (!key) {
      context.leftOut.push(`${context.module}.${part}.${component.key}.${leaf} (no field)`);
      return [];
    }
    const leafSchema = resolve(specOf(context.sources, component), properties[key]);
    const withSource = WITH_SOURCE[typeName]?.includes(leaf) ?? false;
    return [
      {
        name: leaf,
        field: graphqlName(key),
        children: leafSchema?.properties ? stampedLeaves(leafSchema, withSource) : [],
      },
    ];
  });
};

/**
 * Adds `component` to a part of the module, at its path. An object field needs a selection, so a
 * component thrapp reads no fields of is left out.
 */
const addComponent = (
  context: ModuleContext,
  part: ComponentPart,
  component: Component,
  entry: Omit<DefinitionEntry, "path">,
  typeName: string,
): void => {
  const children = selectFields(context, component, part, typeName);
  if (children.length === 0) {
    context.leftOut.push(`${context.module}.${part}.${component.key} (no fields)`);
    return;
  }
  const field = component.path.at(-1) ?? component.key;
  context.output.definitions[part].push({ ...entry, path: component.path });
  context.output.selections[part].push({
    path: component.path.slice(0, -1),
    selection: { name: field, field, children },
  });
};

/** The module's devices and computed values: sensor values, or controller state. */
const addSensorsAndControllerState = (context: ModuleContext): void => {
  for (const component of context.sources.components) {
    if (component.module !== context.module) continue;
    const sensor = SENSOR_TYPES[component.componentType];
    const controller = CONTROLLER_STATE_TYPES[component.componentType];
    if (sensor) {
      const entry = {
        key: component.key,
        componentType: `SensorComponentType.${sensor}`,
        yardTag: component.yardTag,
        valveType: sensor === "Valve" ? `ValveType.${valveType(component.valveType)}` : undefined,
      };
      addComponent(context, "sensorValues", component, entry, sensor);
    } else if (controller) {
      const entry = {
        key: component.key,
        componentType: `ControllerStateComponentType.${controller}`,
      };
      addComponent(context, "controllerState", component, entry, controller);
    } else {
      context.leftOut.push(
        `${context.module}.${component.key} (no type for ${component.componentType})`,
      );
    }
  }
};

/** The thrs-control channel of the module's `kind`, such as `parameters`, if it has one. */
const controllerChannel = (context: ModuleContext, kind: string): Channel | undefined =>
  Object.values(context.sources.thrsControl.channels).find(
    ({ address }) => address === `${CONTROLLER_PREFIX}${context.module}/${kind}`,
  );

/**
 * The actuators thrs-control takes for the module, each a field of its control values topic as
 * thrs-control last actuated it.
 */
const addControlValues = (context: ModuleContext): void => {
  const { thrsControl } = context.sources;
  const channel = controllerChannel(context, "control-values");
  if (!channel) return;
  const path = channel.address.split("/").map(graphqlName);
  for (const [property, actuator] of Object.entries(
    payload(thrsControl, channel)?.properties ?? {},
  )) {
    const control = CONTROL_TYPES[`${actuator.component_type}`];
    // Not an actuator, such as `external_available`.
    if (!control) continue;
    const key = graphqlName(property);
    const component: Component = {
      key,
      module: context.module,
      topic: channel.address,
      path: [...path, key],
      payload: resolve(thrsControl, actuator),
      componentType: `${actuator.component_type}`,
    };
    const entry = {
      key,
      componentType: `ControlComponentType.${control}`,
      yardTag: (actuator.yard_tag as string | null) ?? undefined,
      valveType: actuator.valve_type ? `ValveType.${valveType(actuator.valve_type)}` : undefined,
    };
    addComponent(context, "controlValues", component, entry, control);
  }
};

type ParameterKind = keyof typeof Thrs.ParametersType;

// TODO: placeholder until the thrs-control Spec carries the parameters' kinds or units; copied
// from thrs-api's definitions. Only the numbers: a boolean is Enabled and an array Tuning.
const PARAMETER_KINDS: Record<string, Record<string, ParameterKind>> = {
  adsorption: {
    adsorptionColdMinimum: "Temperature",
    adsorptionColdTrigger: "Temperature",
    adsorptionCoolingSetpoint: "Temperature",
    adsorptionHotMinimum: "Temperature",
    adsorptionHotTrigger: "Temperature",
    hotSupplyTemperatureSetpoint: "Temperature",
    wasteCoolingTemperatureSetpoint: "Temperature",
    wasteRecoveryTemperatureSetpoint: "Temperature",
  },
  consumers: {
    adsorptionFlowRatioSetpoint: "Flow",
    dhwFlowRatioSetpoint: "Flow",
  },
  dc: {
    brightloopFlowSetpoint: "Flow",
    brightloopReturnTemperature: "Temperature",
    maximumSupplyTemperature: "Temperature",
    recoveryTemperature: "Temperature",
    ugridFlowSetpoint: "Flow",
    ugridReturnTemperature: "Temperature",
  },
  dhw: {
    boostingMinimumHeat: "Power",
    boostingStallLockout: "Duration",
    boostingStallWindow: "Duration",
    boostingStartupGrace: "Duration",
    dcFlowcontrolMinimumSetpoint: "FlowControl",
    drivesFlowcontrolMinimumSetpoint: "FlowControl",
    fillingTemperatureSetpoint: "Temperature",
    fullLevelLowerBand: "Level",
    heatpumpFlowSetpoint: "Flow",
    heatpumpTemperatureSetpoint: "Temperature",
    htBoostingFlowSetpoint: "Flow",
    htBoostingMinimumDelta: "dT",
    maximumTankLevel: "Level",
    maximumTankTemperature: "Temperature",
    minimumPumpDutypoint: "Dutypoint",
    minimumTankLevel: "Level",
    minimumTankTemperature: "Temperature",
  },
  drives: {
    propulsionDrivesFlowSetpoint: "Flow",
    propulsionMaximumSupplyTemperature: "Temperature",
    recoveryTemperature: "Temperature",
    shorepowerFlowSetpoint: "Flow",
    shorepowerMaximumSupplyTemperature: "Temperature",
  },
  pcm: {
    gracePeriod: "Duration",
    minimumChargingTemperature: "Temperature",
    pcmChargeFlow: "Flow",
    pcmDischargeFlow: "Flow",
    retryDelay: "Duration",
    stallDuration: "Duration",
  },
  pvt: {
    mainAftMinimumPumpDutypoint: "Dutypoint",
    mainFwdMinimumPumpDutypoint: "Dutypoint",
    maximumSupplyTemperature: "Temperature",
    minimumReturnTemperature: "Temperature",
    ownersMinimumPumpDutypoint: "Dutypoint",
    recoveryActivationStringTemperature: "Temperature",
    recoveryTemperature: "Temperature",
    warmupTemperature: "Temperature",
  },
  thrusters: {
    coolingFlow: "Flow",
    coolingTemperature: "Temperature",
    maximumSupplyTemperature: "Temperature",
    recoveryTemperature: "Temperature",
    thrustersMaximumFlow: "Flow",
    thrustersMinimumFlow: "Flow",
    warmupTemperature: "Temperature",
  },
};

const parameterKind = (module: string, key: string, schema: Schema): ParameterKind =>
  PARAMETER_KINDS[module]?.[key] ??
  (schema.type === "boolean" ? "Enabled" : schema.type === "array" ? "Tuning" : "Ratio");

/** The parameters thrs-control takes for the module, each a field of its parameters topic. */
const addParameters = (context: ModuleContext): void => {
  const { thrsControl } = context.sources;
  const channel = controllerChannel(context, "parameters");
  if (!channel) return;
  const path = channel.address.split("/").map(graphqlName);
  for (const [property, schema] of Object.entries(
    payload(thrsControl, channel)?.properties ?? {},
  )) {
    const key = graphqlName(property);
    context.output.definitions.parameters.push({
      key,
      componentType: `ParametersType.${parameterKind(context.module, key, resolve(thrsControl, schema) ?? schema)}`,
      path: [...path, key],
      description: schema.description,
    });
    context.output.selections.parameters.push({
      path,
      selection: { name: key, field: key, children: [] },
    });
  }
};

/**
 * Fails when two selections of the same component, such as a pump's sensor and control values,
 * give one response name to different fields: a query spreading both fragments merges them.
 */
const checkMergeable = (modules: Record<string, ModuleOutput>): void => {
  const fields = new Map<string, string>();
  const visit = (at: string, { name, field, children }: Selection) => {
    const node = `${at}/${name}`;
    const known = fields.get(node);
    if (known !== undefined && known !== field) {
      throw new Error(`${node} selects both ${known} and ${field}`);
    }
    fields.set(node, field);
    children.forEach((child) => visit(node, child));
  };
  for (const { selections } of Object.values(modules)) {
    for (const { path, selection } of Object.values(selections).flat()) {
      visit(path.join("/"), selection);
    }
  }
};

interface Generated {
  modules: Record<string, ModuleOutput>;
  topics: Record<string, string>;
  leftOut: string[];
}

const generate = (marpower: Spec, thrsControl: Spec): Generated => {
  const all = [
    ...components(marpower, DEVICE_PREFIX, deviceModule, isShown),
    ...components(thrsControl, CONTROLLER_PREFIX, controllerModule),
  ];
  const sources: Sources = { marpower, thrsControl, components: all };
  const leftOut: string[] = [];
  // zero-data's modules and thrs-control's: a module may have devices and no controller.
  const moduleNames = [...new Set(all.map(({ module }) => module))].toSorted();
  const modules = Object.fromEntries(
    moduleNames.map((module) => {
      const output = { definitions: emptyParts(() => []), selections: emptyParts(() => []) };
      const context: ModuleContext = { module, sources, output, leftOut };
      addSensorsAndControllerState(context);
      addControlValues(context);
      addParameters(context);
      return [module, output];
    }),
  );
  checkMergeable(modules);
  return {
    modules,
    topics: Object.fromEntries(all.map(({ key, topic }) => [key, topic])),
    leftOut,
  };
};

// ============================================================================
// Output
// ============================================================================

/**
 * One selection set from selections at their paths, nesting shared path segments once. Branches
 * and components are sorted, the way the definitions sort their components.
 */
const render = (entries: PathSelection[], indent = "  "): string => {
  const branches = lodash.groupBy(
    entries.filter(({ path }) => path.length > 0),
    ({ path }) => path[0],
  );
  const byName = (a: string, b: string) => a.localeCompare(b);
  return [
    ...Object.entries(branches)
      .toSorted(([a], [b]) => byName(a, b))
      .map(
        ([segment, nested]) =>
          `${indent}${segment} {\n${render(
            nested.map(({ path, selection }) => ({ path: path.slice(1), selection })),
            `${indent}  `,
          )}\n${indent}}`,
      ),
    ...entries
      .filter(({ path }) => path.length === 0)
      .toSorted((a, b) => byName(a.selection.name, b.selection.name))
      .map(({ selection }) => renderSelection(selection, indent)),
  ].join("\n");
};

const renderSelection = ({ name, field, children }: Selection, indent: string): string => {
  const head = name === field ? field : `${name}: ${field}`;
  if (children.length === 0) return `${indent}${head}`;
  if (children.every((child) => child.children.length === 0)) {
    return `${indent}${head} { ${children.map((child) => renderSelection(child, "")).join(" ")} }`;
  }
  return `${indent}${head} {\n${children
    .map((child) => renderSelection(child, `${indent}  `))
    .join("\n")}\n${indent}}`;
};

const constName = (module: string, part: Part, suffix: string) =>
  `${screamingSnakeCase(module)}_${screamingSnakeCase(part)}_${suffix}`;

const renderEntry = ({
  key,
  componentType,
  path,
  yardTag,
  valveType,
  description,
}: DefinitionEntry): string =>
  [
    `  ${key}: {`,
    yardTag ? `    yardTag: "${yardTag}",` : undefined,
    `    componentType: ${componentType},`,
    valveType ? `    valveType: ${valveType},` : undefined,
    description ? `    description: ${JSON.stringify(description)},` : undefined,
    `    path: ${JSON.stringify(path)},`,
    "  },",
  ]
    .filter((line) => line !== undefined)
    .join("\n");

/** The type a part's definition must satisfy, so the type check catches a wrong shape. */
const DEFINITION_TYPES: Record<Part, string> = {
  sensorValues: "SensorDefinitions",
  controlValues: "ControlDefinitions",
  parameters: "ParameterDefinitions",
  controllerState: "ControllerStateDefinitions",
};

const write = ({ modules, topics, leftOut }: Generated): void => {
  const header = "// Generated by scripts/generate-mqtt-graphql-queries.ts. Do not edit.";
  // A part without components has no definition or fragment: an empty selection is invalid.
  const definitions = Object.entries(modules).flatMap(([module, { definitions }]) =>
    (Object.entries(definitions) as [Part, DefinitionEntry[]][])
      .filter(([, entries]) => entries.length > 0)
      .map(
        ([part, entries]) =>
          `export const ${constName(module, part, "DEFINITION")} = {\n${entries
            .toSorted((a, b) => a.key.localeCompare(b.key))
            .map(renderEntry)
            .join("\n")}\n} as const satisfies ${DEFINITION_TYPES[part]};`,
      ),
  );
  // Every module with all four parts, as `ModuleDefinition` has them; a part without
  // components is empty.
  const moduleMap = Object.entries(modules)
    .map(
      ([module, { definitions }]) =>
        `  ${module}: {\n${(Object.keys(DEFINITION_TYPES) as Part[])
          .map(
            (part) =>
              `    ${part}: ${definitions[part].length > 0 ? constName(module, part, "DEFINITION") : "{}"},`,
          )
          .join("\n")}\n  },`,
    )
    .join("\n");
  fs.writeFileSync(
    DEFINITIONS_OUTPUT,
    [
      header,
      "import {",
      "  ControlComponentType,",
      "  ControlDefinitions,",
      "  ControllerStateComponentType,",
      "  ControllerStateDefinitions,",
      "  ModuleDefinition,",
      "  ParameterDefinitions,",
      "  ParametersType,",
      "  SensorComponentType,",
      "  SensorDefinitions,",
      "  ValveType,",
      '} from "@/modules/thrapp/types/thrs";',
      "",
      ...definitions.toSorted().flatMap((definition) => [definition, ""]),
      "/** The definitions of every module, by module and part. */",
      `export const MQTT_GRAPHQL_DEFINITIONS = {\n${moduleMap}\n} as const satisfies Record<string, ModuleDefinition>;`,
      "",
      "/** The MQTT topic of each component, by technical name. */",
      `export const MQTT_TOPICS = ${JSON.stringify(topics, null, 2)} as const satisfies Record<string, string>;`,
      "",
      "/** What thrapp would show but the Specs give no thrapp type, field or topic for. */",
      `export const MQTT_GRAPHQL_LEFT_OUT = ${JSON.stringify(leftOut.toSorted(), null, 2)};`,
      "",
    ].join("\n"),
  );

  // A fragment on `Query`: a module part spans several roots (`marpower`, `thrs`), and a view
  // query spreads the fragments it needs (`...DhwSensorValues`).
  const fragmentName = (module: string, part: Part) => `${capitalize(module)}${capitalize(part)}`;
  const queries = Object.entries(modules).flatMap(([module, { selections }]) =>
    (Object.entries(selections) as [Part, PathSelection[]][])
      .filter(([, entries]) => entries.length > 0)
      .map(
        ([part, entries]) =>
          `export const ${constName(module, part, "FRAGMENT")} = \`\nfragment ${fragmentName(module, part)} on Query {\n${render(entries)}\n}\n\`;`,
      ),
  );
  fs.writeFileSync(
    QUERIES_OUTPUT,
    [header, "", ...queries.toSorted().flatMap((query) => [query, ""])].join("\n"),
  );

  if (leftOut.length > 0) {
    console.log(`Left out ${leftOut.length}; see MQTT_GRAPHQL_LEFT_OUT in the definitions.`);
  }
};

const main = (): void => {
  if (!process.argv.includes("--skip-specs")) {
    console.log("Generating the AsyncAPI Specs ...");
    execSync("just generate_specs", { cwd: REPO, stdio: "inherit" });
  }
  write(generate(readSpec("marpower.json"), readSpec("thrs-control.json")));
  // Format like the rest of the code, so a regeneration only differs where the Specs do.
  execSync(`pnpm eslint --fix ${DEFINITIONS_OUTPUT} ${QUERIES_OUTPUT}`, {
    cwd: ZERO_UI,
    stdio: "inherit",
  });
  console.log(
    `Wrote ${path.relative(ZERO_UI, DEFINITIONS_OUTPUT)} and ${path.relative(ZERO_UI, QUERIES_OUTPUT)}.`,
  );
};

if (import.meta.url === `file://${process.argv[1]}`) main();
