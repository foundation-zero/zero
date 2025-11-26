<script lang="ts" setup>
import { cn } from "@common/lib/utils";
import { ArrowRight } from "lucide-vue-next";
import type { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <li
    data-slot="breadcrumb-separator"
    role="presentation"
    aria-hidden="true"
    :class="cn('text-border [&>svg]:size-2.5', props.class)"
  >
    <slot>
      <ArrowRight />
    </slot>
  </li>
</template>
