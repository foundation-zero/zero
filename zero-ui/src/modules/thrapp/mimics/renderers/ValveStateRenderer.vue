<script setup lang="ts">
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { VALVE_OPEN_THRESHOLD } from "../../utils/consts";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<number>>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  {{ (value ?? 0) < VALVE_OPEN_THRESHOLD ? "Closed" : "Open" }}
</template>
