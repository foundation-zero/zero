<script setup lang="ts">
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  <span v-if="value !== undefined">
    {{ value ? "Empty" : "not Empty" }}
  </span>
</template>
