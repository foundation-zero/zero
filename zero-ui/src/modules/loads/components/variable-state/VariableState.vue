<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { PrimitiveProps } from "reka-ui";
import { HTMLAttributes, provide, toRef } from "vue";
import { VariableStateVariants, variableStateVariants } from ".";
import { formatLoadFn } from "../../lib/utils";
import { VariableState, VariableUnit } from "../../types";
import AnimatedNumber from "../animated-number/AnimatedNumber.vue";

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
</script>

<template>
  <span
    data-slot="load-state"
    :class="cn(variableStateVariants({ size, state }), props.class)"
    v-bind="delegatedProps"
  >
    <span data-slot="load-value">
      <animated-number
        :to="props.value!"
        :format="formatLoadFn(props.type)"
      />
    </span>
    <slot />
  </span>
</template>
