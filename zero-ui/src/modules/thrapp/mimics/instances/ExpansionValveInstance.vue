<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { ExpansionValve } from "../components/expansion-valve";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ExpansionValve>
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ExpansionValve"
    :data="props"
  >
    <ExpansionValve v-bind="props" />
    <slot />
  </MimicTooltipTrigger>
</template>
