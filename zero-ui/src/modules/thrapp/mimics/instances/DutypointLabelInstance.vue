<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { Label } from "../components/label/index.ts";
import SensorValue from "../providers/SensorValue.vue";
import { ModuleField } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

defineProps<MimicComponentInstanceProps & { pump: ModuleField<SensorComponentType.Pump> }>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
  >
    {{ tagId }}
    <template #value>
      <SensorValue
        :source="pump"
        field="dutypoint"
      >
        <FieldRenderer.Percentage />
      </SensorValue>
    </template>
  </Label>
</template>
