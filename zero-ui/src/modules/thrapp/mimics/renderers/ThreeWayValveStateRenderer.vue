<script setup lang="ts">
import { computed, toRef } from "vue";
import { FieldRendererProps } from ".";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<number>>();

const value = getFieldValue(toRef(props, "value"));
const label = computed(() => {
  if (value.value === 1) return "AB ↔ A";
  if (value.value === 0) return "AB ↔ B";
  if (value.value === undefined) return "-";
  return "AB ↔ Both";
});
</script>

<template>
  {{ label }}
</template>
