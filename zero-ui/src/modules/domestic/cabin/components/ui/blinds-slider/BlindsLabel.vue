<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { HTMLAttributes } from "vue";
import { getContext } from ".";

defineProps<{
  class?: HTMLAttributes["class"];
}>();

const { control } = getContext();
</script>

<template>
  <label
    data-testid="temperatureSetpointLabel"
    :class="
      cn('text-muted-foreground max-md:text-r3xs md:text-r4xs mt-[1.5em] font-light', $props.class)
    "
    >{{ control.name }}</label
  >
</template>
