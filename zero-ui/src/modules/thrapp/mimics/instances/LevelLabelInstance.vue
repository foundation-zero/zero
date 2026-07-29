<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";

defineProps<
  MimicComponentInstanceProps & {
    level: ModuleField<SensorComponentType.Level>;
  }
>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
  >
    {{ tagId }}
    <template #value>
      <SensorValue
        :source="level"
        field="level"
      >
        <FieldRenderer.Level />
      </SensorValue>
    </template>
  </Label>
</template>
