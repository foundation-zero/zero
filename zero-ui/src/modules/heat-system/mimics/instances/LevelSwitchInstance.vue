<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import LevelSwitch from "../components/level-switch/LevelSwitch.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.LevelSwitch>
>();
const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.LevelSwitch"
    :data="props"
  >
    <LevelSwitch
      v-bind="props"
      :state="state"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
