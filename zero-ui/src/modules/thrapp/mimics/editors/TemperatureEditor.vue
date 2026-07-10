<script setup lang="ts">
import { FieldEditor, NumberEditorProps } from ".";
import { getFieldValue } from "../providers";

const props = withDefaults(defineProps<NumberEditorProps>(), {});
const value = getFieldValue<number>();
</script>

<template>
  <FieldEditor.Number
    v-bind="props"
    v-model="value"
    :min="0"
    :max="100"
    :step="1"
    :format-options="{ unit: 'celsius', style: 'unit' }"
  >
    <slot />
  </FieldEditor.Number>
</template>
