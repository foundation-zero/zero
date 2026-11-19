<script setup lang="ts">
import type { Component } from "vue";
import { useI18n } from "vue-i18n";

defineProps<{
  name: string;
  icon: Component;
  /** Without a route the tile is a planned app, shown disabled. */
  to?: string;
}>();

const { t } = useI18n();
</script>

<template>
  <div
    data-splash-tile
    class="flex w-(--splash-cell) flex-col items-center"
    :class="{ 'coming-soon': !to }"
  >
    <component
      :is="to ? 'RouterLink' : 'div'"
      :to="to"
      class="tile-button flex w-full flex-col items-center rounded-(--splash-radius) pt-3 text-inherit no-underline"
    >
      <span
        class="tile relative grid size-(--splash-tile) place-items-center rounded-(--splash-radius)"
      >
        <component
          :is="icon"
          aria-hidden="true"
          class="icon relative size-(--splash-icon)"
        />
      </span>
      <span
        class="label text-foreground mt-3 text-center text-(length:--splash-label) leading-(--splash-label-line) font-semibold"
      >
        {{ name }}
      </span>
      <span
        v-if="!to"
        class="text-muted-foreground text-center text-(length:--splash-status) leading-normal"
      >
        {{ t("views.splash.comingSoon") }}
      </span>
    </component>
  </div>
</template>

<style scoped>
.tile-button {
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.tile-button:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 4px;
}

/* Glass: translucent body, frosted backdrop, specular rim and a soft top highlight. */
.tile {
  --wash: transparent;
  --glass-inset:
    inset 0 1px 0 var(--splash-glass-rim-hi), inset 0 -10px 18px rgb(0 0 0 / 0.14),
    inset 0 1px 4px color-mix(in srgb, var(--brand) 60%, transparent);
  background: linear-gradient(to bottom, var(--splash-glass-top), var(--splash-glass-bottom));
  border: 1px solid color-mix(in srgb, var(--border) 65%, transparent);
  box-shadow:
    0 4px 20px rgb(0 0 0 / 0.25),
    var(--glass-inset);
  backdrop-filter: blur(5px) saturate(145%) brightness(1.04);
  transition:
    transform 0.15s cubic-bezier(0.2, 0.8, 0.2, 1),
    box-shadow 0.15s ease,
    border-color 0.15s ease;
}

.tile::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background:
    linear-gradient(var(--wash), var(--wash)),
    radial-gradient(130% 70% at 28% -8%, var(--splash-glass-spec), transparent 62%);
  transition: background 0.15s ease;
}

/* Light-catching rim: bright at the top-left edge, a faint return at the bottom-right. */
.tile::after {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  pointer-events: none;
  background: linear-gradient(
    155deg,
    var(--splash-glass-edge-hi) 0%,
    transparent 38%,
    transparent 68%,
    var(--splash-glass-edge-lo) 100%
  );
  mask:
    linear-gradient(#000 0 0) content-box exclude,
    linear-gradient(#000 0 0);
}

.icon {
  color: var(--brand);
  transition: opacity 0.15s ease;
}

@media (hover: hover) {
  :not(.coming-soon) > .tile-button:hover .tile {
    --wash: var(--splash-hover-wash);
    transform: translateY(-4px);
    border: 1.5px solid var(--brand);
    box-shadow:
      0 4px 20px rgb(0 0 0 / 0.25),
      0 0 24px var(--splash-hover-glow),
      var(--glass-inset);
  }
}

:not(.coming-soon) > .tile-button:active .tile {
  --wash: var(--splash-press-wash);
  transform: translateY(2px);
  border: 1.5px solid var(--brand);
  box-shadow: inset 0 3px 10px rgb(0 0 0 / 0.35);
  transition-duration: 0.08s;
}

:not(.coming-soon) > .tile-button:active .icon {
  opacity: 0.85;
}

.coming-soon .tile-button {
  cursor: default;
}

.coming-soon .tile {
  opacity: 0.45;
  border-style: dashed;
}

.coming-soon .label {
  color: var(--muted-foreground);
}

@media (prefers-reduced-motion: reduce) {
  .tile,
  .tile::before,
  .icon {
    transition: none;
  }
}
</style>
