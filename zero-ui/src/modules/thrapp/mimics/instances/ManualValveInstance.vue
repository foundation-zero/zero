<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { ManualValveProps } from "../components/manual-valve";
import ManualValve from "../components/manual-valve/ManualValve.vue";

const props = defineProps<
  MimicComponentInstanceProps &
    ManualValveProps &
    TooltipComponentContext<MimicComponentType.ManualValve>
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ManualValve"
    :data="props"
  >
    <ManualValve v-bind="props" />
  </MimicTooltipTrigger>
</template>
