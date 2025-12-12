<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes, toRefs } from "vue";
import { provideContext } from ".";
import { getLoadState } from "../../lib/utils";
import { ReferenceThresholds, VariableType } from "../../types";
import { Card } from "../card";

const props = defineProps<{
  value: number;
  thresholds?: ReferenceThresholds;
  type: VariableType;
  class?: HTMLAttributes["class"];
}>();

const { value, thresholds, type } = toRefs(props);

const state = computed(() => getLoadState(props.value, props.thresholds));

provideContext({
  state,
  value,
  thresholds,
  type,
});
</script>

<template>
  <Card :class="cn('h-[13.375rem] gap-2', props.class)">
    <slot />
  </Card>
</template>
