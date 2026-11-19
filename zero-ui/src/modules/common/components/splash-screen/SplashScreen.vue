<script setup lang="ts">
import { usePreferredReducedMotion, useResizeObserver } from "@vueuse/core";
import { onBeforeUnmount, onMounted, useTemplateRef } from "vue";
import { useI18n } from "vue-i18n";
import SplashDarkModeToggle from "./SplashDarkModeToggle.vue";
import { SPLASH_GROUPS } from "./splash-screen.consts";
import { fitSplash, playRipple, takeSplashEntry } from "./splash-screen.utils";
import SplashScreenBackground from "./SplashScreenBackground.vue";
import SplashScreenGroup from "./SplashScreenGroup.vue";
import SplashScreenTile from "./SplashScreenTile.vue";
import SplashScreenWordmark from "./SplashScreenWordmark.vue";

const { t } = useI18n();
const entry = takeSplashEntry();
const reducedMotion = usePreferredReducedMotion();
const root = useTemplateRef<HTMLElement>("root");
const header = useTemplateRef<HTMLElement>("header");
const area = useTemplateRef<HTMLElement>("area");
let animations: Animation[] = [];

const fit = () => {
  if (root.value && header.value && area.value) fitSplash(root.value, header.value, area.value);
};

useResizeObserver(root, fit);
onMounted(() => {
  fit();
  if (root.value && reducedMotion.value !== "reduce") animations = playRipple(root.value, entry);
});
onBeforeUnmount(() => animations.forEach((animation) => animation.cancel()));
</script>

<template>
  <div
    ref="root"
    class="splash-screen bg-background text-foreground relative grid min-h-0 flex-1 grid-rows-[auto_1fr] overflow-y-auto"
  >
    <SplashScreenBackground />

    <header
      ref="header"
      class="relative flex justify-center px-(--splash-margin) pt-(--splash-head-top)"
    >
      <SplashScreenWordmark
        :animated="entry === 'cold' && reducedMotion !== 'reduce'"
        class="w-(--splash-wordmark)"
      />
      <SplashDarkModeToggle
        class="absolute top-[calc(var(--splash-head-top)-6px)] right-[calc(var(--splash-margin)*0.6)] max-[560px]:top-7.5 max-[560px]:right-3"
      />
    </header>

    <div
      ref="area"
      class="relative flex [align-items:safe_center] [justify-content:safe_center] px-(--splash-margin) pt-10 pb-12"
    >
      <div
        class="flex max-w-full flex-wrap items-start justify-center gap-x-(--splash-cluster-gap) gap-y-(--splash-line-gap) data-stacked:flex-col data-stacked:flex-nowrap data-stacked:items-stretch"
      >
        <SplashScreenGroup
          v-for="group in SPLASH_GROUPS"
          :key="group.nameKey"
          :name="t(group.nameKey)"
          :count="t('views.splash.appCount', group.tiles.length)"
          :tiles="group.tiles.length"
        >
          <SplashScreenTile
            v-for="tile in group.tiles"
            :key="tile.nameKey"
            :name="t(tile.nameKey)"
            :icon="tile.icon"
            :to="tile.to"
          />
        </SplashScreenGroup>
      </div>
    </div>
  </div>
</template>

<style>
.splash-screen {
  scrollbar-width: none;

  --splash-grid-minor: rgb(68 106 136 / 0.042);
  --splash-grid-major: rgb(68 106 136 / 0.096);
  --splash-vignette: rgb(0 0 0 / 0.12);
  --splash-hover-wash: rgb(255 255 255 / 0.35);
  --splash-press-wash: rgb(0 0 0 / 0.08);
  --splash-hover-glow: rgb(68 106 136 / 0.35);
  --splash-switch-bg: rgb(255 255 255 / 0.7);
  --splash-glass-top: rgb(255 255 255 / 0.62);
  --splash-glass-bottom: rgb(196 203 208 / 0.5);
  --splash-glass-rim-hi: rgb(255 255 255 / 0.7);
  --splash-glass-edge-hi: rgb(255 255 255 / 0.95);
  --splash-glass-edge-lo: rgb(255 255 255 / 0.4);
  --splash-glass-spec: rgb(255 255 255 / 0.35);

  /* Large tiles; the media queries below step down so the launcher fits the screen. */
  --splash-cell: 208px;
  --splash-tile: 168px;
  --splash-radius: 28px;
  --splash-icon: 56px;
  --splash-tile-gap: 16px;
  --splash-cluster-gap: 56px;
  --splash-line-gap: 40px;
  --splash-label: 20px;
  --splash-label-line: 1.6;
  --splash-status: 16px;
  --splash-group-name: 28px;
  --splash-group-count: 16px;
  --splash-rule-accent: 28px;
  --splash-wordmark: 420px;
  --splash-margin: 120px;
  --splash-head-top: 72px;
}

.splash-screen::-webkit-scrollbar {
  display: none;
}

.dark .splash-screen {
  --splash-grid-minor: rgb(153 182 204 / 0.07);
  --splash-grid-major: rgb(153 182 204 / 0.16);
  --splash-vignette: rgb(0 0 0 / 0.28);
  --splash-hover-wash: rgb(255 255 255 / 0.04);
  --splash-press-wash: rgb(0 0 0 / 0.12);
  --splash-hover-glow: rgb(153 182 204 / 0.4);
  --splash-switch-bg: rgb(34 39 43 / 0.6);
  --splash-glass-top: rgb(250 250 250 / 0.07);
  --splash-glass-bottom: rgb(50 57 63 / 0.5);
  --splash-glass-rim-hi: rgb(255 255 255 / 0.14);
  --splash-glass-edge-hi: rgb(255 255 255 / 0.38);
  --splash-glass-edge-lo: rgb(255 255 255 / 0.1);
  --splash-glass-spec: rgb(255 255 255 / 0.08);
}

@media (min-width: 2300px) {
  .splash-screen {
    --splash-wordmark: 560px;
    --splash-margin: 160px;
    --splash-head-top: 96px;
  }
}

@media (min-width: 561px) and (max-height: 900px), (min-width: 1000px) and (max-width: 1500px) {
  .splash-screen {
    --splash-cell: 168px;
    --splash-tile: 136px;
    --splash-radius: 24px;
    --splash-icon: 44px;
    --splash-tile-gap: 12px;
    --splash-cluster-gap: 48px;
    --splash-line-gap: 32px;
    --splash-label: 16px;
    --splash-status: 13px;
    --splash-group-name: 24px;
    --splash-group-count: 14px;
    --splash-wordmark: 320px;
    --splash-margin: 60px;
    --splash-head-top: 44px;
  }
}

@media (max-width: 999px) and (min-height: 901px) {
  .splash-screen {
    --splash-wordmark: 340px;
    --splash-margin: 40px;
    --splash-head-top: 56px;
    --splash-line-gap: 28px;
  }
}

/* Tile sizes chosen by fitSplash, so the launcher fits the screen at any app count. */
.splash-screen[data-splash-size="l"] {
  --splash-cell: 208px;
  --splash-tile: 168px;
  --splash-radius: 28px;
  --splash-icon: 56px;
  --splash-tile-gap: 16px;
  --splash-label: 20px;
  --splash-label-line: 1.6;
  --splash-status: 16px;
  --splash-group-name: 28px;
  --splash-group-count: 16px;
}

.splash-screen[data-splash-size="m"] {
  --splash-cell: 168px;
  --splash-tile: 136px;
  --splash-radius: 24px;
  --splash-icon: 44px;
  --splash-tile-gap: 12px;
  --splash-label: 16px;
  --splash-label-line: 1.6;
  --splash-status: 13px;
  --splash-group-name: 24px;
  --splash-group-count: 14px;
}

.splash-screen[data-splash-size="s"] {
  --splash-cell: 116px;
  --splash-tile: 92px;
  --splash-radius: 18px;
  --splash-icon: 32px;
  --splash-tile-gap: 6px;
  --splash-label: 13px;
  --splash-label-line: 1.4;
  --splash-status: 12px;
  --splash-group-name: 20px;
  --splash-group-count: 13px;
}

@media (max-width: 560px) {
  .splash-screen {
    --splash-cell: 116px;
    --splash-tile: 92px;
    --splash-radius: 18px;
    --splash-icon: 32px;
    --splash-tile-gap: 6px;
    --splash-cluster-gap: 24px;
    --splash-line-gap: 28px;
    --splash-label: 13px;
    --splash-label-line: 1.4;
    --splash-status: 12px;
    --splash-group-name: 20px;
    --splash-group-count: 13px;
    --splash-rule-accent: 20px;
    --splash-wordmark: 200px;
    --splash-margin: 12px;
    --splash-head-top: 40px;
  }
}
</style>
