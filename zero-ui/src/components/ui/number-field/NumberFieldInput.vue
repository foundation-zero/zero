<script setup lang="ts">
import { cn, useAutoFocus } from "@common/lib/utils";
import { NumberFieldInput } from "reka-ui";
import { useTemplateRef, type HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  autofocus?: boolean;
}>();

useAutoFocus<HTMLInputElement>(useTemplateRef("input"), props.autofocus);
</script>

<template>
  <NumberFieldInput
    ref="input"
    autofocus
    data-slot="input"
    :class="
      cn(
        'border-border placeholder:text-muted-foreground focus-visible:ring-brand flex h-9 w-full rounded-md border bg-transparent py-1 text-center text-sm shadow-sm transition-all focus-visible:ring-1 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50',
        props.class,
      )
    "
  />
</template>
