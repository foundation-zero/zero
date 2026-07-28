<script setup lang="ts">
import { ControlValueFields } from "@/modules/thrsim/types";
import { computed } from "vue";
import { FieldEditor } from ".";
import { injectFieldValueField } from "../providers";

const field = injectFieldValueField<ControlValueFields>();

const editor = computed(() => {
  if (!field) return null;

  switch (field) {
    case "temperatureSetpoint":
      return FieldEditor.Temperature;
    case "on":
      return FieldEditor.Toggle;
    case "setpoint":
    case "dutypoint":
      return FieldEditor.Percentage;
    default:
      return null;
  }
});
</script>

<template>
  <component
    :is="editor"
    v-if="editor"
  >
    <slot />
  </component>
</template>
