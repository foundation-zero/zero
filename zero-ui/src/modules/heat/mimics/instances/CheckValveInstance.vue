<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import CheckValve from "../components/check-valve/CheckValve.vue";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.CheckValve>
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.CheckValve"
    :data="props"
  >
    <CheckValve v-bind="props" />
    <slot />
  </MimicTooltipTrigger>
</template>
