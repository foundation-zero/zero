<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { provideMultiLineEditor } from "../../mimics/editors";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  multiline?: boolean;
}>();

provideMultiLineEditor(!!props.multiline);
</script>

<template>
  <li
    :class="
      cn('border-border-subtle text-muted-foreground flex border-b py-2 text-sm', props.class, {
        'flex-col items-start gap-1 pt-1': props.multiline,
        'items-center justify-between': !props.multiline,
      })
    "
  >
    <slot />
  </li>
</template>
