import { Component } from "@/@types/thrs";
import { MqttClient } from "@/mqtt";
import $RefParser, { JSONSchema } from "@apidevtools/json-schema-ref-parser";
import { JSONSchemaObject } from "@apidevtools/json-schema-ref-parser/dist/lib/types";
import { defineStore } from "pinia";
import { EMPTY, map, Observable } from "rxjs";
import { ref } from "vue";

const parse = map((msg: string) => JSON.parse(msg));

export type SimulationState =
  | "available"
  | "mode_picking"
  | "value_setting"
  | "ready_to_start"
  | "ready_to_run"
  | "ran";
export interface StatusMessage {
  status: SimulationState;
}

export interface AllowedModesMessage {
  modes: string[];
}

export interface SchemaMessage {
  sensors: object;
  controls: object;
  simulation_inputs: object;
  simulation_inputs_values: object;
  control_params: object;
  control_modes: object;
}

export type FieldType = "number" | "boolean" | "string";

export type TypeToType<T extends FieldType> = T extends "number"
  ? number
  : T extends "boolean"
    ? boolean
    : T extends "string"
      ? string
      : never;

export interface Field<T extends FieldType> {
  name: string;
  type: T;
  default?: TypeToType<T>;
  minimum?: number;
  maximum?: number;
  description?: string;
  items?: string[];
  set: <V extends object>(src: V, value: TypeToType<T>) => V;
  get: (src: object) => TypeToType<T> | undefined;
}

export type UndeterminedType = TypeToType<FieldType>;
export type UndeterminedField = Field<FieldType>;

export const extractField = (name: string, value: JSONSchemaObject): UndeterminedField =>
  ({
    name,
    type: value.type as FieldType,
    default: value.default,
    minimum: value.minimum,
    maximum: value.maximum,
    items: value.enum,
    description: value.description,
    set: (src: Record<string, object>, val: UndeterminedType) => ({
      ...src,
      [name]: val,
    }),
    get: (src: Record<string, UndeterminedType>) => {
      if (name in src) {
        return src[name] as UndeterminedType;
      }
      return undefined;
    },
  }) as UndeterminedField;

export const parseSchema = async (schema: object): Promise<UndeterminedField[]> => {
  const expanded = await $RefParser.dereference(schema);
  if (!("properties" in expanded || typeof expanded.properties !== "object")) {
    throw new Error("Schema does not contain properties");
  }
  return Object.entries(expanded.properties as object).map(([name, value]) =>
    extractField(name, value as JSONSchemaObject),
  );
};

export interface SchemaComponent {
  name: string;
  fields: UndeterminedField[];
}

// Extracts stamped fields from a JSON schema
const extractFields = (schema: JSONSchema): UndeterminedField[] => {
  if (!("properties" in schema && typeof schema.properties === "object")) {
    throw new Error("Schema does not contain properties");
  }
  return Object.entries(schema.properties).map(([name, value]) => {
    if (
      !(
        "properties" in value &&
        typeof value.properties === "object" &&
        "value" in value.properties &&
        "timestamp" in value.properties
      )
    ) {
      throw new Error(`Field ${name} does not contain properties`);
    }
    return {
      name,
      type: value.properties.value.type as FieldType,
      default: value.properties.value.default,
      minimum: value.properties.value.minimum,
      maximum: value.properties.value.maximum,
      items: value.properties.value.enum,
      description: value.description,
      set: (src: object, val: number) => ({
        ...src,
        [name]: {
          value: val,
          timestamp: new Date().toISOString(),
        },
      }),
      get: (src: Record<string, { value: UndeterminedType; timestamp: string }>) => {
        if (name in src && "value" in src[name] && "timestamp" in src[name]) {
          return (src[name] as { value: number; timestamp: string }).value;
        }
        return undefined;
      },
    };
  }) as UndeterminedField[];
};

export const parseSchemaNested = async (schema: object): Promise<SchemaComponent[]> => {
  const expanded = await $RefParser.dereference(schema);
  if (!("properties" in expanded && typeof expanded.properties === "object")) {
    throw new Error("Schema does not contain properties");
  }

  return Object.entries(expanded.properties).map(([name, value]) => ({
    name,
    fields: extractFields(value as JSONSchema).map((field) => ({
      ...field,
      set: (src: Record<string, UndeterminedType>, val: number) => ({
        ...src,
        [name]: field.set(src[name] || {}, val),
      }),
      get: (src: Record<string, Record<string, UndeterminedType>>) => field.get(src[name] || {}),
    })),
  })) as SchemaComponent[];
};

export const useThrsStore = defineStore("THRS", () => {
  const sensorValues = ref<Observable<Component>>(EMPTY);
  const controlValues = ref<Observable<Component>>(EMPTY);
  const simulationStatus = ref<Observable<StatusMessage>>(EMPTY);
  const allowedModes = ref<Observable<AllowedModesMessage>>(EMPTY);
  const sendMessage = ref<(topic: string, payload: object) => Promise<void>>(async () => {});
  const schemas = ref<Observable<SchemaMessage>>(EMPTY);

  const initialize = async () => {
    const client = await MqttClient.connect("ws://localhost:5173/thrs-ws");
    sensorValues.value = client.topic("thrs/sensor_values").pipe(parse);
    controlValues.value = client.topic("thrs/control_values").pipe(parse);
    simulationStatus.value = client.topic("thrs/simulation/status").pipe(parse);
    allowedModes.value = client.topic("thrs/simulation/allowed_modes").pipe(parse);
    schemas.value = client.topic("thrs/simulation/schemas").pipe(parse);
    sendMessage.value = async (topic: string, payload: object) => {
      await client.publish(topic, payload);
    };
  };

  return {
    sensorValues,
    controlValues,
    simulationStatus,
    allowedModes,
    schemas,
    sendMessage,
    initialize,
  };
});
