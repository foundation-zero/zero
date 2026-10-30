<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { Fahrenheit, FahrenheitMode } from "../components/fahrenheit";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.AdsorptionChiller>
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <Fahrenheit
      v-bind="forwardedProps"
      :state="state"
    >
      <template #tag>
        <YardTag>{{ tooltip?.yardTag }}</YardTag>
      </template>
      <template #title>
        {{ tooltip?.title }}
      </template>
      <template #badge>
        <FahrenheitMode :source="source" />
      </template>

      <slot />
    </Fahrenheit>
  </MimicTooltipTrigger>
</template>
