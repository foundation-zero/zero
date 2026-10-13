<script setup lang="ts">
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { HeatPumpMode, HeatPumpModes } from "../components/heat-pump";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  <HeatPumpMode :mode="value ? HeatPumpModes.Active : HeatPumpModes.Inactive" />
</template>
