<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { useVModel } from "@vueuse/core";
import type { HTMLAttributes } from "vue";

const props = defineProps<{
  defaultValue?: string | number;
  modelValue?: string | number;
  class?: HTMLAttributes["class"];
  invalid?: boolean;
}>();

const emits = defineEmits<{
  (e: "update:modelValue", payload: string | number): void;
}>();

const modelValue = useVModel(props, "modelValue", emits, {
  passive: true,
  defaultValue: props.defaultValue,
});
</script>

<template>
  <input
    v-model="modelValue"
    data-slot="input"
    :aria-invalid="props.invalid ? 'true' : 'false'"
    :class="
      cn(
        'file:text-input-foreground text-input-foreground placeholder:text-input-muted-foreground selection:bg-primary selection:text-primary-foreground border-input-muted-border bg-input-muted flex h-9 w-full min-w-0 rounded-xs border px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm',
        'focus-visible:border-input-border focus-visible:bg-input focus-visible:text-input-foreground focus-visible:ring-ring/50 focus-visible:ring-[1px]',
        'aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive',
        props.class,
      )
    "
  />
</template>
