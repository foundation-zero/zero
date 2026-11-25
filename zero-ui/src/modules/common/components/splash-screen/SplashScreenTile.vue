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
      class="tile-button flex w-full flex-col items-center rounded-(--splash-radius) pt-(--splash-tile-pad) text-inherit no-underline"
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
        class="label text-foreground mt-(--splash-tile-pad) text-center text-(length:--splash-label) leading-(--splash-label-line) font-semibold"
      >
        {{ name }}
      </span>
      <span
        v-if="!to"
        class="text-muted-foreground text-center text-(length:--splash-status) leading-(--splash-status-line)"
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

/*
 * Frosted glass, fading from a trace of foreground to dull. Figma blends color and opacity apart, which
 * darkens (or in dark mode lightens) the middle; CSS gradients don't, so the stops spell that out.
 */
.tile {
  --wash: transparent;
  --edge: 1px;
  --inner-shadow: inset 0 1px 4px var(--brand);
  --mix-25: color-mix(in srgb, var(--dull) 25%, var(--foreground));
  --mix-50: color-mix(in srgb, var(--dull) 50%, var(--foreground));
  --mix-75: color-mix(in srgb, var(--dull) 75%, var(--foreground));
  background:
    linear-gradient(var(--wash), var(--wash)) border-box,
    linear-gradient(
        to bottom,
        color-mix(in srgb, var(--foreground) 2.5%, transparent),
        color-mix(in srgb, var(--mix-25) 14.4%, transparent) 25%,
        color-mix(in srgb, var(--mix-50) 26.3%, transparent) 50%,
        color-mix(in srgb, var(--mix-75) 38.1%, transparent) 75%,
        color-mix(in srgb, var(--dull) 50%, transparent)
      )
      border-box;
  border: var(--edge) solid var(--border);
  box-shadow: 0 4px 20px rgb(0 0 0 / 0.25);
  backdrop-filter: blur(2px);
  transition:
    transform 0.15s cubic-bezier(0.2, 0.8, 0.2, 1),
    box-shadow 0.15s ease,
    border-color 0.15s ease;
}

/* Drawn over the border, as Figma does, so the edge stays one crisp line. */
.tile::after {
  content: "";
  position: absolute;
  inset: calc(var(--edge) * -1);
  border-radius: inherit;
  pointer-events: none;
  box-shadow: var(--inner-shadow);
}

.icon {
  color: var(--brand);
  transition: opacity 0.15s ease;
}

@media (hover: hover) {
  :not(.coming-soon) > .tile-button:hover .tile {
    --wash: rgb(255 255 255 / 0.04);
    transform: translateY(-4px);
    --edge: 1.5px;
    border-color: var(--brand);
    box-shadow:
      0 4px 20px rgb(0 0 0 / 0.25),
      0 0 24px color-mix(in srgb, var(--brand) 40%, transparent);
  }
}

:not(.coming-soon) > .tile-button:active .tile {
  --wash: rgb(0 0 0 / 0.12);
  transform: translateY(2px);
  --edge: 1.5px;
  --inner-shadow: inset 0 3px 10px rgb(0 0 0 / 0.35), inset 0 1px 4px var(--brand);
  border-color: var(--brand);
  box-shadow: none;
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
  .icon {
    transition: none;
  }
}
</style>
