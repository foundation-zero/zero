<script setup lang="ts">
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { HTMLWrapper } from "../components/html-wrapper/index.ts";
import ExchangeCircuit from "./components/ExchangeCircuit.vue";
import { MimicComponentInstanceProps } from "./index.ts";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.ExchangeCircuit> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: 196,
    height: 200,
    forceHeight: true,
  },
);
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ExchangeCircuit"
    :data="props"
  >
    <HTMLWrapper v-bind="{ width, height, forceHeight, x, y }">
      <ExchangeCircuit
        class="w-full"
        v-bind="{ sensors, controllerState, controls, parameters, source, tooltip, custom }"
      />
    </HTMLWrapper>
    <slot />
  </MimicTooltipTrigger>
</template>
