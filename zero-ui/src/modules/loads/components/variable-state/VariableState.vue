<script setup lang="ts">
import { cn, formatInt, useFixed } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { PrimitiveProps } from "reka-ui";
import { computed, HTMLAttributes, provide, toRef } from "vue";
import { VariableStateVariants, variableStateVariants } from ".";
import { formatLoadFn } from "../../lib/utils";
import { VariableState, VariableUnit } from "../../types";
import AnimatedNumber from "@/modules/common/components/animated-number/AnimatedNumber.vue";

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

const splitValue = useFixed(
  toRef(props, "value"),
  computed(() => (props.value != null && Math.abs(props.value) < 1 ? 2 : 1)),
);
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

      <template v-if="splitValue[1] != undefined">
        <span class="text-r2xs!">.</span>
        <animated-number
          v-for="(fraction, index) in splitValue[1]"
          :key="index"
          class="text-r2xs"
          data-slot="load-value"
          :to="fraction"
          :format="formatInt"
        />
      </template>
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
