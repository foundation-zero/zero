<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { MimicComponentState } from "../components";
import { PumpProps, PumpState } from "../components/pump";
import Pump from "../components/pump/Pump.vue";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ManualPump> & PumpProps
>();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <Pump
      v-bind="forwardedProps"
      :pump-state="PumpState.Inactive"
      :state="MimicComponentState.Manual"
      :manual="true"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
