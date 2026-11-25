<script setup lang="ts">
import { RiMoonLine, RiSunLine } from "@remixicon/vue";
import { computed, toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useUIStore } from "../../stores/ui";

const { t } = useI18n();
const { colorMode } = toRefs(useUIStore());
const { setColorMode } = useUIStore();

const target = computed(() => (colorMode.value === "dark" ? "light" : "dark"));
</script>

<template>
  <button
    type="button"
    class="text-brand focus-visible:outline-brand grid size-13.5 cursor-pointer place-items-center rounded-xl bg-(--splash-switch-bg) focus-visible:outline-2 focus-visible:outline-offset-4 max-[999px]:size-11"
    :aria-label="t(`views.splash.switchTo.${target}`)"
    @click="setColorMode(target)"
  >
    <component
      :is="target === 'dark' ? RiMoonLine : RiSunLine"
      aria-hidden="true"
      class="size-9 max-[999px]:size-7.5"
    />
  </button>
</template>
