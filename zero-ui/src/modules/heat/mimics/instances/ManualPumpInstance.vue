<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { MimicComponentState } from "../components";
import { PumpProps, PumpState } from "../components/pump";
import Pump from "../components/pump/Pump.vue";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ManualPump> & PumpProps
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ManualPump"
    :data="props"
  >
    <Pump
      v-bind="props"
      :pump-state="PumpState.Inactive"
      :state="MimicComponentState.Manual"
      :manual="true"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
