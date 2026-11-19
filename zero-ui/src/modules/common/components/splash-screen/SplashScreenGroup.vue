<script setup lang="ts">
defineProps<{
  name: string;
  count: string;
}>();
</script>

<template>
  <section
    :aria-label="name"
    class="flex max-w-full flex-col"
  >
    <div
      data-splash-head
      class="relative mb-4 flex items-baseline gap-3 pb-3 pl-1"
    >
      <h2
        class="font-headers text-foreground text-(length:--splash-group-name) leading-[1.2] font-medium"
      >
        {{ name }}
      </h2>
      <span class="text-muted-foreground text-(length:--splash-group-count)">{{ count }}</span>
      <span class="rule absolute inset-x-0 bottom-0 h-px" />
    </div>
    <div class="tiles flex flex-wrap gap-x-(--splash-tile-gap) gap-y-3">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.tiles {
  max-width: min(
    100%,
    calc(
      var(--splash-columns, 99) * var(--splash-cell) + (var(--splash-columns, 99) - 1) *
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
