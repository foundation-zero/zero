<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { PrimitiveProps } from "reka-ui";
import { computed, HTMLAttributes, provide, toRef } from "vue";
import { VariableStateVariants, variableStateVariants } from ".";
import { formatLoad } from "../../lib/utils";
import { VariableState, VariableType } from "../../types";

type VariableStateProps = PrimitiveProps & {
  value: number | undefined;
  state: VariableState;
  size?: VariableStateVariants["size"];
  type: VariableType;
  class?: HTMLAttributes["class"];
};

const props = defineProps<VariableStateProps>();
const delegatedProps = reactiveOmit(props, "class");
const formattedLoad = computed(() => formatLoad(props.value, props.type));
const type = toRef(props, "type");

provide("load-type", type);
</script>

<template>
  <span
    data-slot="load-state"
    :class="cn('relative', variableStateVariants({ size, state }), props.class)"
    v-bind="delegatedProps"
  >
    <span data-slot="load-value">
      {{ formattedLoad }}
    </span>
    <slot />
  </span>
</template>
