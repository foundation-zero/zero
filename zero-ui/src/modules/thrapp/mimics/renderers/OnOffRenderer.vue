<script setup lang="ts">
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  {{ value ? "On" : "Off" }}
</template>
