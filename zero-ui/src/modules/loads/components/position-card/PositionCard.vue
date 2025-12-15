<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { ReferenceThresholds, VariableType } from "../../types";
import { VariableCard } from "../variable-card";

const props = defineProps<{
  value: number;
  thresholds?: ReferenceThresholds;
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <VariableCard
    :type="VariableType.Percentage"
    :value="value"
    :thresholds="thresholds"
    :class="cn('h-[13.375rem] w-[21rem]', props.class)"
  >
    <slot />
  </VariableCard>
</template>
