<script setup lang="ts">
import { useI18n } from "vue-i18n";
import {
  HERO_DESCRIPTION_DELAY,
  HERO_DESCRIPTION_DURATION,
  HERO_KICKER_DELAY,
  HERO_KICKER_DURATION,
  HERO_LETTERS_DURATION,
  HERO_LETTERS_INITIAL_DELAY,
  HERO_LETTERS_INTERVAL,
  SPLASH_APP_LINKS,
  SPLASH_LETTERS,
  TILE_ANIMATION_INTERVAL,
  TILE_INITIAL_DELAY,
} from "./";
import SplashScreenBackground from "./background/SplashScreenBackground.vue";
import SplashScreenHeader from "./header/SplashScreenHeader.vue";
import SplashScreenHeaderBrand from "./header/SplashScreenHeaderBrand.vue";
import SplashScreenHero from "./hero/SplashScreenHero.vue";
import SplashScreenHeroDescription from "./hero/SplashScreenHeroDescription.vue";
import SplashScreenHeroKicker from "./hero/SplashScreenHeroKicker.vue";
import SplashScreenHeroLetters from "./hero/SplashScreenHeroLetters.vue";
import SplashDarkModeToggle from "./SplashDarkModeToggle.vue";
import SplashScreenTile from "./tile/SplashScreenTile.vue";
import SplashScreenTileAction from "./tile/SplashScreenTileAction.vue";
import SplashScreenTileCard from "./tile/SplashScreenTileCard.vue";
import SplashScreenTileContent from "./tile/SplashScreenTileContent.vue";
import SplashScreenTileDescription from "./tile/SplashScreenTileDescription.vue";
import SplashScreenTileHeader from "./tile/SplashScreenTileHeader.vue";
import SplashScreenTileIcon from "./tile/SplashScreenTileIcon.vue";
import SplashScreenTileTitle from "./tile/SplashScreenTileTitle.vue";

const { t } = useI18n();
</script>

<template>
  <main
    class="bg-background text-foreground relative min-h-screen overflow-hidden"
    style="isolation: isolate"
  >
    <SplashScreenBackground />

    <div class="relative z-10 flex min-h-screen flex-col px-4 py-4 sm:px-6 lg:px-8 lg:py-6">
      <SplashScreenHeader>
        <SplashScreenHeaderBrand>
          {{ t("views.splash.brand") }}
        </SplashScreenHeaderBrand>
        <SplashDarkModeToggle />
      </SplashScreenHeader>

      <section class="mx-auto flex w-full max-w-7xl flex-1 flex-col justify-center py-10 lg:py-16">
        <SplashScreenHero>
          <SplashScreenHeroKicker
            :animation-delay="HERO_KICKER_DELAY"
            :animation-duration="HERO_KICKER_DURATION"
          >
            {{ t("views.splash.kicker") }}
          </SplashScreenHeroKicker>
          <SplashScreenHeroLetters
            :letters="SPLASH_LETTERS"
            :animation-duration="HERO_LETTERS_DURATION"
            :animation-interval="HERO_LETTERS_INTERVAL"
            :animation-delay="HERO_LETTERS_INITIAL_DELAY"
          />
          <SplashScreenHeroDescription
            :animation-delay="HERO_DESCRIPTION_DELAY"
            :animation-duration="HERO_DESCRIPTION_DURATION"
          >
            {{ t("views.splash.description") }}
          </SplashScreenHeroDescription>
        </SplashScreenHero>

        <div class="mt-12 grid gap-4 md:mt-16 md:grid-cols-2 xl:grid-cols-3">
          <SplashScreenTile
            v-for="(appLink, index) in SPLASH_APP_LINKS"
            :key="appLink.id"
            :to="appLink.to"
            :animation-delay="TILE_INITIAL_DELAY + index * TILE_ANIMATION_INTERVAL"
            :animation-duration="TILE_ANIMATION_INTERVAL"
          >
            <SplashScreenTileCard
              :border="appLink.border"
              :shadow="appLink.shadow"
              :glow="appLink.glow"
            >
              <SplashScreenTileHeader>
                <SplashScreenTileIcon
                  :icon="appLink.icon"
                  :background="appLink.iconBackground"
                />
                <SplashScreenTileAction>
                  {{ t("views.splash.open") }}
                </SplashScreenTileAction>
              </SplashScreenTileHeader>

              <SplashScreenTileContent>
                <SplashScreenTileTitle>
                  {{ t(appLink.nameKey) }}
                </SplashScreenTileTitle>

                <SplashScreenTileDescription>
                  {{ t(appLink.descriptionKey) }}
                </SplashScreenTileDescription>
              </SplashScreenTileContent>
            </SplashScreenTileCard>
          </SplashScreenTile>
        </div>
      </section>
    </div>
  </main>
</template>

<style>
@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
