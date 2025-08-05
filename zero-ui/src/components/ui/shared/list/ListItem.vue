<script setup lang="ts">
import { cn } from "@/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ selected?: boolean; class?: HTMLAttributes["class"] }>();
</script>

<template>
  <li
    class=""
    :class="[
      cn(
        [
          'border-primary/5 flex items-center justify-between gap-2 border px-6 py-4 transition-colors disabled:pointer-events-none disabled:opacity-50',
        ],
        props.class,
      ),
      {
        'font-bold': selected,
        'font-light': !selected,
      },
    ]"
  >
    <slot />
  </li>
</template>
