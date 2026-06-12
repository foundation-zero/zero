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
        'flex items-center justify-between gap-x-2.5 py-1 last-of-type:pb-2',
        {
          'text-muted-foreground bg-dull px-4 text-sm first-of-type:pt-2 last-of-type:mb-2 has-[+_[data-item-default]]:pb-2 [&+_[data-item-default]]:pt-2':
            props.size === 'sm',
          'text-foreground text-base first-of-type:py-3! has-[+_[data-item-sm]]:pb-2 [&+_[data-item-sm]]:pt-2':
            props.size === 'default',
        },
        props.class,
      )
    "
  >
    <slot />
  </li>
</template>
