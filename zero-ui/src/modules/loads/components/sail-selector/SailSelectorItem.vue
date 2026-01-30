<script setup lang="ts">
import Toggle from "@/components/ui/toggle/Toggle.vue";
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
const modelValue = defineModel<boolean>({ required: true });
</script>

<template>
  <Toggle
    v-model="modelValue"
    variant="outline"
    :class="cn(props.class)"
  >
    <slot />
  </Toggle>
</template>
