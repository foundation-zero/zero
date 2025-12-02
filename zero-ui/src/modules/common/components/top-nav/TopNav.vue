<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useScrollOffset } from ".";

const { t } = useI18n();

const title = ref<HTMLElement | null>(null);
const scrollOffset = useScrollOffset(title);
</script>

<template>
  <nav
    class="fixed right-0 left-0 flex flex-col justify-between overflow-hidden backdrop-blur-md"
    :style="{ top: scrollOffset }"
  >
    <h1
      ref="title"
      class="py-3 text-center text-xl font-bold tracking-widest"
    >
      {{ t("app.title") }}
    </h1>
    <slot />
  </nav>
</template>

<style lang="scss" scoped>
nav::before {
  content: "";
  position: absolute;
  top: -200%;
  left: -25%;
  width: 150%;
  height: 500%;
  z-index: -1;
  opacity: 0.9;

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
