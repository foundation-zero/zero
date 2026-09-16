<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { MODE_COLORS, ModeBadgeMode, ModeBadgeSize, SIZE_ATTRIBUTES } from ".";

const props = withDefaults(
  defineProps<{ mode: ModeBadgeMode; label?: string; size: ModeBadgeSize }>(),
  {},
);

const color = computed(() => {
  return MODE_COLORS[props.mode];
});

const size_attributes = computed(() => {
  return SIZE_ATTRIBUTES[props.size];
});

const t = tScoped("thrapp.mimics.modeBadge.modes");
</script>

<template>
  <div
    class="text-inverse-foreground bg-attention inline px-4 font-medium transition-colors"
    :style="{
      backgroundColor: color,
    }"
    :class="size_attributes"
  >
    <span v-if="label === undefined">{{ t(mode) }}</span>
    <span v-else>{{ label }}</span>
  </div>
</template>
