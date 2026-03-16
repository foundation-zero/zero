<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <div
    :class="
      cn(
        '-mt-1 flex w-full py-1 font-medium capitalize transition-colors',

        props.class,
      )
    "
  >
    <span class="min-h-4.5 overflow-x-hidden overflow-ellipsis whitespace-nowrap">
      <slot />
    </span>
  </div>
</template>
