<script setup lang="ts">
import { ControlComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { ModuleField } from "../providers";
import ControlValue from "../providers/ControlValue.vue";
import { FieldRenderer } from "../renderers";

defineProps<MimicComponentInstanceProps & { pump: ModuleField<ControlComponentType.Pump> }>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
    min-width="45"
  >
    {{ tagId }}
    <template #value>
      <ControlValue
        :source="pump"
        field="dutypoint"
      >
        <FieldRenderer.Percentage />
      </ControlValue>
    </template>
  </Label>
</template>
