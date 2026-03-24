<script setup lang="ts">
import { cn, formatInt, useFixed } from "@/modules/common/lib/utils";
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

const splitValue = useFixed(toRef(props, "value"), 1);
</script>

<template>
  <span
    data-slot="load-state"
    :class="cn(variableStateVariants({ size, state }), 'items-baseline', props.class)"
    v-bind="delegatedProps"
  >
    <template v-if="type === VariableUnit.Tonne">
      <animated-number
        data-slot="load-value"
        :to="splitValue[0]"
        :format="formatInt"
      />

      <animated-number
        v-if="splitValue[1] != undefined"
        class="text-r2xs"
        data-slot="load-value"
        :to="splitValue[1]"
        :format="(val: number) => `.${formatInt(val)}`"
      />
    </template>
    <template v-else>
      <animated-number
        data-slot="load-value"
        :to="value"
        :format="formatLoadFn(type)"
      />
    </template>
    <slot />
  </span>
</template>
