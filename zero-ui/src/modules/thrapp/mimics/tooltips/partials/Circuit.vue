<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { useTranslations } from "..";
import { isSensorField, ModuleField, SensorValue } from "../../providers";
import * as Partials from "./";

const { items, sources } = useTranslations();

defineProps<{
  source: ModuleField<SensorComponentType.HeatExchanger>;
}>();
</script>

<template>
  <SensorValue
    :source="source"
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
    :source="source"
    field="temperatureSupply"
  >
    <Partials.ListItem size="sm">
      {{ items("incomingTemperature") }}
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="temperatureReturn"
  >
    <Partials.ListItem size="sm">
      {{ items("outgoingTemperature") }}
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="flow"
  >
    <Partials.ListItem>
      {{ items("flow") }}
      <template
        v-if="isSensorField(source, SensorComponentType.CalculatedFlow)"
        #sourceName
      >
        {{ sources("calculated") }}
      </template>
    </Partials.ListItem>
  </SensorValue>
</template>
