<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { injectMultiLineEditor } from "@modules/thrapp/mimics/editors";
import { injectValueForm } from "@modules/thrapp/mimics/providers/forms";
import { HTMLAttributes } from "vue";

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
