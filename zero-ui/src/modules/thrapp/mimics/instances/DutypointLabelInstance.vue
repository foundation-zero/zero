<script setup lang="ts">
import { ControlComponentType } from "@/modules/thrsim/types";
import { Label } from "../components/label/index.ts";
import ControlValue from "../providers/ControlValue.vue";
import { ModuleField } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

defineProps<MimicComponentInstanceProps & { pump: ModuleField<ControlComponentType.Pump> }>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
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
