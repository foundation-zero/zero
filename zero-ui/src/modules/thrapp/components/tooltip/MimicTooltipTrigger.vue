<script setup lang="ts" generic="Type extends MimicComponentType">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { getTooltipContext, TooltipComponentContext } from ".";
import { TOOLTIPS } from "../../mimics/tooltips";
import { MimicComponentType } from "../../types";

const props = defineProps<{
  data: TooltipComponentContext<Type> & Record<string, unknown>;
}>();

const router = useRouter();
const { disabled } = getTooltipContext();

// Components without a registered tooltip (yet) render as plain content instead of a dead trigger.
const interactive = computed(() => !disabled && !!props.data.type && !!TOOLTIPS[props.data.type]);

const setTooltip = () => {
  if (interactive.value && props.data.registerField) {
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
    v-if="interactive"
    class="origin-center transition-all will-change-auto transform-fill hover:scale-105 hover:cursor-pointer hover:drop-shadow-2xl hover:drop-shadow-black"
    @click="setTooltip"
  >
    <slot />
  </g>
  <slot v-else />
</template>
