<script setup lang="ts">
import { ControlValueFields, SensorValueFields } from "@/modules/thrs/types";
import { computed } from "vue";
import { FieldRenderer } from ".";
import { injectFieldValueField } from "../providers";

const field = injectFieldValueField<ControlValueFields | SensorValueFields>();

const editor = computed(() => {
  if (!field) return null;

  switch (field) {
    case "temperature":
    case "temperatureSetpoint":
      return FieldRenderer.Temperature;
    case "on":
      return FieldRenderer.OnOff;
    case "deltaT":
      return FieldRenderer.DeltaT;
    case "flow":
      return FieldRenderer.FlowRate;
    case "setpoint":
      return FieldRenderer.ValveState;
    case "positionRel":
    case "dutypoint":
      return FieldRenderer.Percentage;
    case "heat":
      return FieldRenderer.Heat;
    case "level":
      return FieldRenderer.Level;
  }

  return null;
});
</script>

<template>
  <component
    :is="editor"
    v-if="editor"
    v-bind="$props"
  >
    <slot />
  </component>
</template>
