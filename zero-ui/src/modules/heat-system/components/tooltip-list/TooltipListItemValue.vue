<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { useAdvisoryEnabled, useAutomaticMode } from "../../state";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const isAutomaticMode = useAutomaticMode();
const isAdvisoryEnabled = useAdvisoryEnabled();
</script>

<template>
  <span
    data-slot="value"
    :class="
      cn(
        'border-b border-dashed px-2 pb-0.5 whitespace-nowrap',
        {
          'border-attention-muted': isAutomaticMode || !isAdvisoryEnabled,
          'border-warning': !isAutomaticMode && !isAdvisoryEnabled,
        },
        props.class,
      )
    "
  >
    <slot />
  </span>
</template>
