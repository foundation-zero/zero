<script setup lang="ts" generic="Type extends MimicComponentType">
import { useRouter } from "vue-router";
import { getTooltipContext, TooltipComponentContext } from ".";
import { findTooltipContext } from "../../mimics/data";
import { MimicComponentType } from "../../types";

const props = defineProps<{
  type: Type;
  data: TooltipComponentContext<Type> & Record<string, unknown>;
}>();

const router = useRouter();
const { disabled } = getTooltipContext();

const setTooltip = () => {
  console.log(
    "set tooltip",
    props.data.registerField,
    findTooltipContext(props.data.registerField!),
  );
  if (!disabled && props.data.source) {
    router.push({
      query: {
        ...router.currentRoute.value.query,
        tooltip: String(props.data.registerField),
        type: props.data.type,
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
