<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { useTranslations } from "..";
import { isField, isSensorField, ModuleField, SensorValue } from "../../providers";
import * as Partials from "./";

const { items, sources } = useTranslations();

defineProps<{
  deltaT?: ModuleField<SensorComponentType.DeltaT | SensorComponentType.HeatExchanger>;
  incoming: ModuleField<
    SensorComponentType.Temperature | SensorComponentType.CalculatedTemperature
  >;
  outgoing: ModuleField<
    SensorComponentType.Temperature | SensorComponentType.CalculatedTemperature
  >;
  flow?: ModuleField<SensorComponentType.Flow | SensorComponentType.CalculatedFlow>;
}>();
</script>

<template>
  <SensorValue
    v-if="isField(deltaT)"
    :source="deltaT"
    field="deltaT"
  >
    <Partials.ListItem>
      {{ items("deltaTemperature") }}
      <template #sourceName>
        {{ sources("calculated") }}
      </template>
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="incoming"
    field="temperature"
  >
    <Partials.ListItem size="sm">
      {{ items("incomingTemperature") }}
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="outgoing"
    field="temperature"
  >
    <Partials.ListItem size="sm">
      {{ items("outgoingTemperature") }}
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    v-if="isField(flow)"
    :source="flow"
    field="flow"
  >
    <Partials.ListItem>
      {{ items("flow") }}
      <template
        v-if="isSensorField(flow, SensorComponentType.CalculatedFlow)"
        #sourceName
      >
        {{ sources("calculated") }}
      </template>
    </Partials.ListItem>
  </SensorValue>
</template>
