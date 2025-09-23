<script setup lang="ts">
import { Client, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { GraphQLField, GraphQLNonNull, GraphQLObjectType, StringValueNode } from "graphql";
import { type Component, computed, ref, Ref } from "vue";
import PumpControl from "./controls/PumpControl.vue";
import ValveControl from "./controls/ValveControl.vue";
import ValueTable from "./ValueTable.vue";

const props = defineProps<{
  module: string;
  schema: GraphQLField<unknown, unknown, unknown>;
  client: Client;
}>();

const COMPONENTS: Record<"pump" | "valve", Component> = {
  pump: PumpControl,
  valve: ValveControl,
};

const componentsQuery = (objectType: GraphQLObjectType) =>
  Object.entries(objectType.getFields())
    .map(([key, value]) => {
      const fieldsQuery = Object.keys(
        (value.type as GraphQLNonNull<GraphQLObjectType>).ofType.getFields(),
      )
        .map(
          (field) => `${field} {
        value
        timestamp
        }`,
        )
        .join("\n    ");
      return `${key} {
        ${fieldsQuery}
    }`;
    })
    .join("\n");

const queryFor = (objectType: Ref<GraphQLObjectType>, name: string) =>
  computed(() => {
    return `query ${props.module}Values {
    modules {
      ${props.module} {
        ${name} {
          ${componentsQuery(objectType.value)}
        }
      }
    }
  }`;
  });

const queryPacked = (query: Ref<string>, fieldName: string) => {
  const { data, ...rest } = useQuery({ query });
  return computed(() => ({ data: data.value?.modules[props.module][fieldName], ...rest }));
};

const sensorValuesQuery = queryFor(
  computed(
    () =>
      (
        (props.schema.type as GraphQLNonNull<GraphQLObjectType>).ofType.getFields().sensorValues
          .type as GraphQLNonNull<GraphQLObjectType>
      ).ofType,
  ),
  "sensorValues",
);
const sensorValues = queryPacked(sensorValuesQuery, "sensorValues");
const controlValueSchema = computed(
  () =>
    (
      (props.schema.type as GraphQLNonNull<GraphQLObjectType>).ofType.getFields().controlValues
        .type as GraphQLNonNull<GraphQLObjectType>
    ).ofType,
);
const controlValuesQuery = queryFor(controlValueSchema, "controlValues");
const controlValuesComponentsQuery = computed(() => componentsQuery(controlValueSchema.value));
const controlValuesFromQuery = queryPacked(controlValuesQuery, "controlValues");
const controlValuesFromMutation = ref<{ data: Record<string, unknown> } | null>(null);
const controlValues = computed(
  () => controlValuesFromMutation.value ?? controlValuesFromQuery.value,
);

useIntervalFn(
  async () => {
    await sensorValues.value.executeQuery();
    await controlValuesFromQuery.value.executeQuery();
    controlValuesFromMutation.value = null;
  },
  5000,
  { immediateCallback: true },
);

const controlComponents = computed(() => {
  if (controlValueSchema.value) {
    return Object.entries(controlValueSchema.value.getFields())
      .map(([key, value]) => {
        const directive = value?.astNode?.directives?.find(
          (directive) => directive.name.value == "jsonSchemaDirective",
        );
        const componentType = (
          directive?.arguments?.find((argument) => argument.name.value == "componentType")
            ?.value as StringValueNode
        ).value;
        const yardTag = (
          directive?.arguments?.find((argument) => argument.name.value == "yardTag")
            ?.value as StringValueNode
        ).value;
        const valveType = (
          directive?.arguments?.find((argument) => argument.name.value == "valveType")
            ?.value as StringValueNode
        ).value;
        if (componentType && componentType in COMPONENTS) {
          return {
            key,
            componentType,
            yardTag,
            valveType,
            component: COMPONENTS[componentType as "pump" | "valve"],
          };
        } else {
          return null;
        }
      })
      .filter((v) => v !== null);
  }
  return [];
});

const setControlValues = (newValues: Record<string, unknown>) => {
  controlValuesFromMutation.value = { data: newValues };
};
</script>
<template>
  <div v-if="controlValues.data && sensorValues.data">
    <div
      v-for="control in controlComponents"
      :key="control.key"
    >
      <component
        :is="control.component"
        v-if="
          control.component && controlValues.data[control.key] && sensorValues.data[control.key]
        "
        :sensor-values="sensorValues.data[control.key]"
        :control-values="controlValues.data[control.key]"
        :component-name="control.key"
        :component-type="control.componentType"
        :control-values-query="controlValuesComponentsQuery"
        :yard-tag="control.yardTag"
        :valve-type="control.valveType"
        :module="module"
        @update:control-values="setControlValues"
      />
    </div>
    <ValueTable
      v-if="sensorValues.data"
      :values="sensorValues.data"
      :format="(value: number) => value.toFixed(2)"
    />
  </div>
</template>
