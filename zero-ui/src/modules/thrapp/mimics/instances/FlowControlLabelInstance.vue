<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
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
    min-width="55"
    height="50"
  >
    {{ tagId }}
    <template #value>
      <SensorValue
        :source="valve"
        field="positionRel"
      >
        <FieldRenderer.Percentage />
      </SensorValue>
    </template>
  </Label>
</template>
