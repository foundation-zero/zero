<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { HTMLWrapper } from "../components/html-wrapper";
import { getMimicDataProvider } from "../providers";
import ConnectingCircuit from "./content/ConnectingCircuitContent.vue";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.ConnectingCircuit> & {
        width?: number | string;
        height?: number | string;

        inverted?: boolean;
      }
  >(),
  { inverted: false },
);

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ConnectingCircuit"
    :data="props"
  >
    <HTMLWrapper v-bind="{ width, height, x, y }">
      <ConnectingCircuit
        v-bind="{
          sensors,
          controllerState,
          controls,
          parameters,
          source,
          tooltip,
          custom,
          inverted,
        }"
        :state="state"
      >
        <slot />
      </ConnectingCircuit>
    </HTMLWrapper>
  </MimicTooltipTrigger>
</template>
