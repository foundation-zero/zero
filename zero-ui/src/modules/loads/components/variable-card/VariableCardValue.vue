<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { getContext } from ".";
import { VariableState as VariableStateDisplay, VariableUnit } from "../variable-state";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const { value, state, type } = getContext();
</script>

<template>
  <VariableStateDisplay
    :type="type"
    size="xl"
    :value="value"
    :state="state"
    :class="cn('-mt-1', props.class)"
  >
    <VariableUnit />
  </VariableStateDisplay>
</template>
