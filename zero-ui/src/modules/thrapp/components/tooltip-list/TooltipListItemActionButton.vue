<script setup lang="ts">
import Button from "@/components/ui/button/Button.vue";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <Button
    data-slot="action"
    :class="props.class"
  >
    <slot />
  </Button>
</template>
