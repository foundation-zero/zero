<script setup lang="ts">
import { cn, formatInt } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { PrimitiveProps } from "reka-ui";
import { computed, HTMLAttributes, provide, toRef } from "vue";
import { VariableStateVariants, variableStateVariants } from ".";
import { formatLoad, splitLoad } from "../../lib/utils";
import { VariableState, VariableUnit } from "../../types";

type VariableStateProps = PrimitiveProps & {
  value?: number | null;
  state: VariableState;
  size?: VariableStateVariants["size"];
  type: VariableUnit;
  class?: HTMLAttributes["class"];
};

const props = defineProps<VariableStateProps>();
const delegatedProps = reactiveOmit(props, "class");
const type = toRef(props, "type");

provide("load-type", type);

const splitValue = computed(() => (props.value == undefined ? undefined : splitLoad(props.value)));
</script>

<template>
  <span
    data-slot="load-state"
    :class="cn(variableStateVariants({ size, state }), 'items-baseline', props.class)"
    v-bind="delegatedProps"
  >
    <template v-if="type === VariableUnit.Tonne && splitValue != undefined">
      <span data-slot="load-value">{{ splitValue.sign }}{{ formatInt(splitValue.integer) }}</span>
      <span
        class="text-r2xs"
        data-slot="load-value"
        >.{{ formatInt(splitValue.fraction).padStart(splitValue.fractionDigits, "0") }}</span
      >
    </template>
    <template v-else>
      <span data-slot="load-value">{{ formatLoad(value, type) }}</span>
    </template>
    <slot />
  </span>
</template>
