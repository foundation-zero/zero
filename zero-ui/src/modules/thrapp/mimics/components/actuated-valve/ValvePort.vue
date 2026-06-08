<script setup lang="ts">
import { PortProps } from ".";
import { getMimicComponentContext, MimicComponentState } from "..";

defineProps<PortProps>();

const { stateColor, state } = getMimicComponentContext();
</script>

<template>
  <path
    :d="d"
    class="fill-dull"
  />
  <path
    :d="d"
    :fill-opacity="flow"
    class="fill-attention transition-all duration-300"
    :stroke="stateColor"
    :stroke-width="state === MimicComponentState.Normal ? 1 : 2"
  />
</template>
