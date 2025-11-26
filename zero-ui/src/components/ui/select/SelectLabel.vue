<script setup lang="ts">
import { cn } from "@common/lib/utils";
import type { SelectLabelProps } from "reka-ui";
import { SelectLabel } from "reka-ui";
import type { HTMLAttributes } from "vue";

const props = defineProps<SelectLabelProps & { class?: HTMLAttributes["class"] }>();
</script>

<template>
  <SelectLabel
    data-slot="select-label"
    :class="cn('text-disabled-foreground px-4 py-3 text-xs font-medium', props.class)"
  >
    <slot />
  </SelectLabel>
</template>
