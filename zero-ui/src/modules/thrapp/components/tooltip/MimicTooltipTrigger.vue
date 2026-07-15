<script setup lang="ts" generic="Type extends MimicComponentType">
import { useRouter } from "vue-router";
import { getTooltipContext, TooltipComponentContext } from ".";
import { MimicComponentType } from "../../types";

const props = defineProps<{
  type: Type;
  data: TooltipComponentContext<Type> & Record<string, unknown>;
}>();

const router = useRouter();
const { disabled } = getTooltipContext();

const setTooltip = () => {
  if (!disabled && props.data.source) {
    router.push({
      query: { tooltip: props.data.source?.join(".") },
    });
  }
};
</script>

<template>
  <g
    v-if="!disabled"
    class="origin-center transition-all transform-fill hover:scale-105 hover:cursor-pointer hover:drop-shadow-2xl hover:drop-shadow-black"
    @click="setTooltip"
  >
    <slot />
  </g>
  <slot v-else />
</template>
