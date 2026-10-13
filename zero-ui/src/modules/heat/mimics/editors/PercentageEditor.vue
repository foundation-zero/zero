<script setup lang="ts">
import { ratioAsPercentage } from "@/modules/common/lib/utils";
import { FieldEditor, NumberEditorProps } from ".";
import { getFieldValue } from "../providers";

const props = withDefaults(defineProps<NumberEditorProps>(), {
  min: 0,
  max: 100,
  step: 1,
});

const value = getFieldValue<number>();
const percentage = ratioAsPercentage(value);
</script>

<template>
  <FieldEditor.Number
    v-bind="props"
    v-model="percentage"
    :format-options="{ unit: 'percent', style: 'unit' }"
  >
    <slot />
  </FieldEditor.Number>
</template>
