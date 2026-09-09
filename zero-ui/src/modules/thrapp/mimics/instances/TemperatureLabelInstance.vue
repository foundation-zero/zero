<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types/index.ts";
import { MimicComponentInstanceProps } from ".";
import { Label, LabelProps } from "../components/label";
import { ModuleField } from "../providers";
import SensorValue from "../providers/SensorValue.vue";
import { FieldRenderer } from "../renderers";

defineProps<
  MimicComponentInstanceProps &
    LabelProps & { temperature: ModuleField<SensorComponentType.Temperature> }
>();
</script>

<template>
  <Label v-bind="$props">
    {{ tagId }}
    <template #value>
      <SensorValue
        :source="temperature"
        field="temperature"
      >
        <FieldRenderer.Temperature />
      </SensorValue>
    </template>
  </Label>
</template>
