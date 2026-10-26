<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { PvtString } from "../components/pvt-string";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.PvtString>
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <PvtString v-bind="forwardedProps">{{ custom.label }}</PvtString>
    <slot />
  </MimicTooltipTrigger>
</template>
