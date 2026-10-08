<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { HTMLWrapper } from "../components/html-wrapper";
import FreshwaterCircuitContent from "./content/FreshwaterCircuitContent.vue";

const props = defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.FreshwaterCircuit> & {
      width?: number | string;
      height?: number | string;
    }
>();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.FreshwaterCircuit"
    :data="props"
  >
    <HTMLWrapper v-bind="{ width, height, x, y }">
      <FreshwaterCircuitContent
        v-bind="{ sensors, controllerState, controls, parameters, source, tooltip, custom }"
      >
        <template
          v-for="(_, slotName) in $slots"
          :key="slotName"
          #[slotName]
        >
          <slot :name="slotName" />
        </template>
      </FreshwaterCircuitContent>
    </HTMLWrapper>
  </MimicTooltipTrigger>
</template>
