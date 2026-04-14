<script setup lang="ts">
import { useTemplateRef } from "vue";
import { TopNavToolbar, useScrollOffset } from ".";
import { AppLauncher } from "../app-launcher";
import { DarkModeToggle } from "../dark-mode";
import TopNavZero from "./TopNavZero.vue";

const title = useTemplateRef("title");
const scrollOffset = useScrollOffset(title);
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
        <template #right-content>
          <DarkModeToggle />
          <AppLauncher />
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
