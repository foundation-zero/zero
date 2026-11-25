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
    class="splash-screen text-foreground relative grid min-h-0 flex-1 grid-rows-[auto_1fr] overflow-y-auto bg-(--splash-background)"
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
        class="absolute top-(--splash-switch-top) right-(--splash-switch-right)"
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

  /* The design's light launcher sits on neutral white rather than the app's cool grey-0. */
  --splash-background: var(--color-neutral-0);

  --splash-grid-minor: 4%;
  --splash-grid-major: 10%;
  --splash-vignette: rgb(0 0 0 / 0.09);
  --splash-switch-bg: var(--muted);

  /* Large tiles; the media queries below step down so the launcher fits the screen. */
  --splash-cell: 208px;
  --splash-tile: 168px;
  --splash-radius: 28px;
  --splash-icon: 56px;
  --splash-tile-gap: 16px;
  --splash-cluster-gap: 56px;
  --splash-line-gap: 40px;
  --splash-label: 20px;
  --splash-label-line: 36px;
  --splash-status: 16px;
  --splash-status-line: 32px;
  --splash-tile-pad: 12px;
  --splash-group-name: 24px;
  --splash-group-count: 16px;
  --splash-rule-accent: 28px;
  --splash-wordmark: 420px;
  --splash-margin: 120px;
  --splash-head-top: 72px;
  --splash-switch-top: 76px;
  --splash-switch-right: 120px;
}

.splash-screen::-webkit-scrollbar {
  display: none;
}

.dark .splash-screen {
  --splash-background: var(--background);
  --splash-grid-minor: 7%;
  --splash-grid-major: 16%;
  --splash-vignette: rgb(0 0 0 / 0.21);
  --splash-switch-bg: color-mix(in srgb, var(--background) 50%, transparent);
}

@media (min-width: 2300px) {
  .splash-screen {
    --splash-wordmark: 560px;
    --splash-margin: 160px;
    --splash-head-top: 96px;
    --splash-switch-top: 101px;
    --splash-switch-right: 96px;
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
    --splash-label-line: 32px;
    --splash-status: 12px;
    --splash-status-line: 20px;
    --splash-tile-pad: 10px;
    --splash-wordmark: 320px;
    --splash-margin: 60px;
    --splash-head-top: 44px;
    --splash-switch-top: 36px;
    --splash-switch-right: 48px;
  }
}

@media (max-width: 999px) and (min-height: 901px) {
  .splash-screen {
    --splash-wordmark: 340px;
    --splash-margin: 40px;
    --splash-head-top: 35px;
    --splash-switch-top: 33px;
    --splash-switch-right: 38px;
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
  --splash-label-line: 36px;
  --splash-status: 16px;
  --splash-status-line: 32px;
  --splash-tile-pad: 12px;
}

.splash-screen[data-splash-size="m"] {
  --splash-cell: 168px;
  --splash-tile: 136px;
  --splash-radius: 24px;
  --splash-icon: 44px;
  --splash-tile-gap: 12px;
  --splash-label: 16px;
  --splash-label-line: 32px;
  --splash-status: 12px;
  --splash-status-line: 20px;
  --splash-tile-pad: 10px;
}

.splash-screen[data-splash-size="s"] {
  --splash-cell: 116px;
  --splash-tile: 92px;
  --splash-radius: 18px;
  --splash-icon: 32px;
  --splash-tile-gap: 6px;
  --splash-label: 12px;
  --splash-label-line: 20px;
  --splash-status: 12px;
  --splash-status-line: 20px;
  --splash-tile-pad: 8px;
}

@media (max-width: 560px) {
  .splash-screen {
    --splash-cell: 116px;
    --splash-tile: 92px;
    --splash-radius: 18px;
    --splash-icon: 32px;
    --splash-tile-gap: 6px;
    --splash-cluster-gap: 24px;
    --splash-line-gap: 32px;
    --splash-label: 12px;
    --splash-label-line: 20px;
    --splash-status: 12px;
    --splash-status-line: 20px;
    --splash-tile-pad: 8px;
    --splash-group-name: 20px;
    --splash-group-count: 13px;
    --splash-rule-accent: 20px;
    --splash-wordmark: 200px;
    --splash-margin: 12px;
    --splash-head-top: 22px;
    --splash-switch-top: 12px;
    --splash-switch-right: clamp(8px, 50vw - 152px, 24px);
  }
}
</style>
