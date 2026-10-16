<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { ExpansionTank } from "../components/expansion-tank";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ExpansionTank>
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ExpansionTank"
    :data="props"
  >
    <ExpansionTank v-bind="props" />
    <slot />
  </MimicTooltipTrigger>
</template>
