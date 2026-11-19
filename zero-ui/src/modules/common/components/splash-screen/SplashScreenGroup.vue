<script setup lang="ts">
import { useId } from "vue";

defineProps<{
  name: string;
  count: string;
  /** Number of tiles, so the group is exactly as wide as its tile grid. */
  tiles: number;
}>();

const headingId = useId();
</script>

<template>
  <section
    :aria-labelledby="headingId"
    class="flex max-w-full flex-col"
  >
    <div
      data-splash-head
      class="relative mb-4 flex items-baseline gap-3 pb-3 pl-1"
    >
      <h2
        :id="headingId"
        class="font-headers text-foreground text-(length:--splash-group-name) leading-[1.2] font-medium"
      >
        {{ name }}
      </h2>
      <span class="text-muted-foreground text-(length:--splash-group-count)">{{ count }}</span>
      <span class="rule absolute inset-x-0 bottom-0 h-px" />
    </div>
    <div
      class="tiles flex flex-wrap gap-x-(--splash-tile-gap) gap-y-3"
      :style="{ '--splash-group-columns': `min(var(--splash-columns, 99), ${tiles})` }"
    >
      <slot />
    </div>
  </section>
</template>

<style scoped>
/* A fixed grid width keeps the heading rule flush with the tiles and wrapped rows left-aligned. */
.tiles {
  width: min(
    100%,
    calc(
      var(--splash-group-columns) * var(--splash-cell) + (var(--splash-group-columns) - 1) *
        var(--splash-tile-gap)
    )
  );
}

/* Neutral, with a short brand accent, so it reads as a heading underline rather than a grid line. */
.rule {
  background: color-mix(in srgb, var(--foreground) 32%, transparent);
}

.rule::before {
  content: "";
  position: absolute;
  left: 0;
  bottom: -1px;
  width: var(--splash-rule-accent);
  height: 3px;
  border-radius: 2px;
  background: var(--brand);
}
</style>
