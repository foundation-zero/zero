<script setup lang="ts">
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
    :class="props.class"
  >
    <VariableUnit />
  </VariableStateDisplay>
</template>
