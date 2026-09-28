<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";

defineProps<MimicComponentInstanceProps & { valve: ModuleField<SensorComponentType.Valve> }>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
    :width="60"
    :height="50"
  >
    {{ tagId }}
    <template #value>
      <span>A:</span>
      <SensorValue :source="valve">
        <FieldRenderer.Auto />
      </SensorValue>
    </template>
  </Label>
</template>
