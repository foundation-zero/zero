<script setup lang="ts" generic="Type extends MimicComponentType">
import { getTooltipContext, TooltipComponentContext } from ".";
import { TOOLTIPS } from "../../mimics/tooltips";
import { MimicComponentType } from "../../types";

defineProps<{
  type: Type;
  data: TooltipComponentContext<Type> & Record<string, unknown>;
}>();

const { setTooltip, disabled } = getTooltipContext();
</script>

<template>
  <g
    v-if="!disabled"
    class="origin-center transition-all transform-fill hover:scale-105 hover:cursor-pointer hover:drop-shadow-2xl hover:drop-shadow-black"
    @click="setTooltip(data, TOOLTIPS[type])"
  >
    <slot />
  </g>
  <slot v-else />
</template>
