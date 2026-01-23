<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

// const { modelValue } = injectRootContext();
const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div
    data-slot="sail-selector-position"
    :class="cn('-mx-4 flex flex-nowrap gap-2 p-4', props.class)"
  >
    <slot />
  </div>
</template>
