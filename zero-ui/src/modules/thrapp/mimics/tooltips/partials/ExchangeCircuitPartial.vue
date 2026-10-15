<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { useTranslations } from "..";
import { ModuleField, SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers";
import * as Partials from "./";

const { items, sources } = useTranslations();

defineProps<{
  source: ModuleField<SensorComponentType.HeatTransferDevice>;
}>();
</script>

<template>
  <SensorValue
    :source="source"
    field="heat"
  >
    <Partials.ListItem>
      {{ items("heatExchange") }}
      <template #source>
        <FieldRenderer.Source no-link>({{ sources("calculated") }})</FieldRenderer.Source>
      </template>
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="deltaT"
  >
    <Partials.ListItem no-source>
      {{ items("deltaTemperature") }}
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="temperatureSupply"
  >
    <Partials.ListItem size="sm">
      {{ items("incomingTemperature") }}
      <template #source>
        <FieldRenderer.Source api-only />
      </template>
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="temperatureReturn"
  >
    <Partials.ListItem size="sm">
      {{ items("outgoingTemperature") }}
      <template #source>
        <FieldRenderer.Source api-only />
      </template>
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="source"
    field="flow"
  >
    <Partials.ListItem>
      {{ items("flow") }}
      <template #source>
        <FieldRenderer.Source api-only />
      </template>
    </Partials.ListItem>
  </SensorValue>
</template>
