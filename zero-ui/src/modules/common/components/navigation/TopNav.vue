<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { RiArrowLeftLine } from "@remixicon/vue";
import { toRefs, useTemplateRef } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { TopNavToolbar, useScrollOffset } from ".";
import { AppLauncher } from "../app-launcher";
import { DarkModeToggle } from "../dark-mode";
import TopNavZero from "./TopNavZero.vue";

const { meta, query } = toRefs(useRoute());
const title = useTemplateRef("title");
const scrollOffset = useScrollOffset(title);

const { t } = useI18n();
</script>

<template>
  <nav
    data-slot="top-nav"
    class="fixed right-0 left-0 flex flex-col justify-between overflow-hidden backdrop-blur-md"
    :style="{ top: scrollOffset }"
  >
    <slot name="header">
      <TopNavToolbar
        ref="title"
        class="border-0"
      >
        <template
          v-if="query.returnUrl"
          #left-content
        >
          <RouterLink :to="{ name: query.returnUrl.toString() }">
            <Button
              variant="secondary"
              class="flex items-center rounded-full max-md:p-0 max-sm:size-7 sm:gap-1"
            >
              <RiArrowLeftLine class="inline size-4" />
              <span class="max-sm:hidden">{{ t("labels.back") }}</span>
            </Button>
          </RouterLink>
        </template>
        <template #right-content>
          <DarkModeToggle />
          <AppLauncher v-if="!meta.hideAppSwitcher" />
        </template>
        <template #center>
          <TopNavZero />
        </template>
      </TopNavToolbar>
    </slot>

    <slot />
  </nav>
</template>

<style lang="scss" scoped>
[data-slot="top-nav"]::before {
  content: "";
  position: absolute;
  top: -200%;
  left: -25%;
  width: 150%;
  height: 500%;
  z-index: -1;
  opacity: 0.9;
}

:global(.dark [data-slot="top-nav"]::before) {
  // This gradient was provided by the design team (@Wadim)
  background:
    radial-gradient(
      43.74% 35.44% at 50.03% 36.53%,
      var(----general---brand-dull, rgba(86, 133, 169, 0.2)) 0%,
      rgba(153, 182, 204, 0) 100%
    ),
    var(----general---background-muted, #121619);
}
</style>
