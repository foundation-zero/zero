<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { injectMultiLineEditor } from "../../mimics/editors";
import { injectValueForm } from "../../mimics/providers/forms";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const form = injectValueForm();
const isMultiLineEditor = injectMultiLineEditor();
</script>

<template>
  <span
    :class="
      cn(
        'text-muted-foreground flex items-center text-sm',
        { 'text-disabled-foreground': form?.isPending.value, 'w-full': isMultiLineEditor },
        props.class,
      )
    "
  >
    <slot />
  </span>
</template>
