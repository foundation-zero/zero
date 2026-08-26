<script setup lang="ts">
import { BoilerTankState } from "@/modules/thrsim/types";
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { BoilerTankMode } from "../components/boiler-tank";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<BoilerTankState>>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  <BoilerTankMode :mode="value" />
</template>
