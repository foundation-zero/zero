<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    size?: "sm" | "default";
  }>(),
  {
    size: "default",
  },
);
</script>

<template>
  <li
    :[`data-item-${props.size}`]="true"
    :class="
      cn(
        'flex items-center justify-between gap-x-2.5 last-of-type:pb-2',
        {
          'text-muted-foreground bg-dull px-4 py-1 text-sm first-of-type:pt-2 last-of-type:mb-2 has-[+_[data-item-default]]:pb-2 [&+_[data-item-default]]:pt-2':
            props.size === 'sm',
          'text-foreground py-2 text-base first-of-type:pt-3! last-of-type:pb-3 [&+_[data-item-default]]:pt-1 [&+_[data-item-sm]]:pt-2':
            props.size === 'default',
        },
        props.class,
      )
    "
  >
    <slot />
  </li>
</template>
