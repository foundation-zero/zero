<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { PyranoMeterDot } from "../components/pyrano-meter";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.Pyranometer>
>();
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <PyranoMeterDot
      :x="x"
      :y="y"
    />
  </MimicTooltipTrigger>
</template>
