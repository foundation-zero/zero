<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";

defineProps<
  MimicComponentInstanceProps & {
    pressure: ModuleField<SensorComponentType.Pressure>;
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
        :source="pressure"
        field="pressure"
      >
        <FieldRenderer.Pressure />
      </SensorValue>
    </template>
  </Label>
</template>
