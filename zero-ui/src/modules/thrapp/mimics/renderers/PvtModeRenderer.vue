<script setup lang="ts">
import { PvtMode as PvtModeEnum } from "@/modules/thrsim/types";
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { PvtMode } from "../components/pvt";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<PvtModeEnum>>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  <PvtMode :mode="value ?? PvtModeEnum.Idle" />
</template>
