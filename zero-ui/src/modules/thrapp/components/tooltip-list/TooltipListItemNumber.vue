<script setup lang="ts">
import { NumberFormatter } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { HTMLAttributes } from "vue";
import TooltipListItemValue from "./TooltipListItemValue.vue";

const props = defineProps<{
  value?: number;
  class?: HTMLAttributes["class"];
  format?: NumberFormatter;
  unit?: string;
  dense?: boolean;
}>();
</script>

<template>
  <TooltipListItemValue :class="props.class">
    <AnimatedNumber
      :to="value"
      :format="format"
    />
    <span
      v-if="unit"
      :class="{ 'pl-0.5': !dense }"
      >{{ unit }}</span
    >
    <slot />
  </TooltipListItemValue>
</template>
