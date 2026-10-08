<script setup lang="ts">
import { cn, formatInt } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { PrimitiveProps } from "reka-ui";
import { computed, HTMLAttributes, provide, toRef } from "vue";
import { VariableStateVariants, variableStateVariants } from ".";
import { formatLoadFn, splitLoad } from "../../lib/utils";
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

const splitValue = computed(() => (props.value == undefined ? undefined : splitLoad(props.value)));
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
        :to="splitValue?.integer"
        :format="(val: number) => `${splitValue?.sign}${formatInt(val)}`"
      />

      <animated-number
        v-if="splitValue != undefined"
        class="text-r2xs"
        data-slot="load-value"
        :to="splitValue.fraction"
        :format="
          (val: number) => `.${formatInt(val).padStart(splitValue?.fractionDigits ?? 1, '0')}`
        "
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
