<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { RiCheckLine, RiHourglassLine, RiInfinityLine } from "@remixicon/vue";
import { type Component, computed } from "vue";
import { MODE_COLORS, ModeBadgeMode, ModeBadgeSize, SIZE_ATTRIBUTES } from ".";

const props = withDefaults(
  defineProps<{ mode: ModeBadgeMode; label?: string; size: ModeBadgeSize; icon?: boolean }>(),
  {},
);

const color = computed(() => {
  return MODE_COLORS[props.mode];
});

const size_attributes = computed(() => {
  return SIZE_ATTRIBUTES[props.size];
});

const t = tScoped("thrapp.mimics.modeBadge.modes");

const icons: Partial<Record<ModeBadgeMode, Component>> = {
  [ModeBadgeMode.Idle]: RiHourglassLine,
  [ModeBadgeMode.Active]: RiCheckLine,
  [ModeBadgeMode.AlwaysActive]: RiInfinityLine,
};
</script>

<template>
  <div
    class="text-inverse-foreground bg-attention inline-flex items-center gap-1 px-4 font-medium text-nowrap transition-colors"
    :style="{
      backgroundColor: color,
    }"
    :class="size_attributes"
  >
    <component
      :is="icons[mode]"
      v-if="icon"
      class="size-4"
    />

    <span v-if="label === undefined">{{ t(mode) }}</span>
    <span v-else>{{ label }}</span>
  </div>
</template>
