<script setup lang="ts" generic="Type extends MimicComponentType">
import { useRouter } from "vue-router";
import { getTooltipContext, TooltipComponentContext } from ".";
import { MimicComponentType } from "../../types";

const props = defineProps<{
  data: TooltipComponentContext<Type> & Record<string, unknown>;
}>();

const router = useRouter();
const { disabled } = getTooltipContext();

const setTooltip = () => {
  if (!disabled && props.data.registerField && props.data.type) {
    router.push({
      query: {
        ...router.currentRoute.value.query,
        tooltip: String(props.data.registerField),
        type: props.data.type,
        index: props.data.index != undefined && props.data.index > 0 ? props.data.index : undefined,
      },
    });
  }
};
</script>

<template>
  <g
    v-if="!disabled"
    class="origin-center transition-all will-change-auto transform-fill hover:scale-105 hover:cursor-pointer hover:drop-shadow-2xl hover:drop-shadow-black"
    @click="setTooltip"
  >
    <slot />
  </g>
  <slot v-else />
</template>
