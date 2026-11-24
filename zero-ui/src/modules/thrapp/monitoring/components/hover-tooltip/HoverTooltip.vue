<script setup lang="ts">
import { TOOLTIP_CLASS } from "@/modules/thrapp/monitoring/monitoring.consts";
import { useWindowSize } from "@vueuse/core";

// Keeps the tooltip, up to max-w-72 wide, inside the window near its sides.
const { width: windowWidth } = useWindowSize();

/**
 * The design system tooltip, following the pointer. It renders on top of the
 * page, so the edge of a tile never cuts it off; it sits above the pointer and
 * flips below it near the top of the window.
 */
const props = defineProps<{
  /** Pointer position in the window (clientX / clientY); null hides it. */
  at: { x: number; y: number } | null;
}>();
</script>

<template>
  <Teleport to="body">
    <div
      v-if="props.at"
      role="tooltip"
      :class="[TOOLTIP_CLASS, 'pointer-events-none fixed z-50 w-max max-w-72']"
      :style="{
        left: `${Math.min(Math.max(props.at.x, 150), windowWidth - 150)}px`,
        top: `${props.at.y}px`,
        transform: `translate(-50%, ${props.at.y < 96 ? '16px' : 'calc(-100% - 12px)'})`,
      }"
    >
      <slot />
    </div>
  </Teleport>
</template>
