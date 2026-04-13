<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { RiContrast2Line, RiMoonLine, RiSunLine } from "@remixicon/vue";
import { BasicColorSchema } from "@vueuse/core";
import { type Component, toRefs } from "vue";
import { useUIStore } from "../../stores/ui";

const { darkMode } = toRefs(useUIStore());
const { setColorMode } = useUIStore();

const MODES = ["light", "auto", "dark"] as const;

const ICONS: Record<BasicColorSchema, Component> = {
  light: RiSunLine,
  dark: RiMoonLine,
  auto: RiContrast2Line,
};

const cycleTheme = () => {
  const currentIndex = MODES.indexOf(darkMode.value);
  const nextMode = MODES[(currentIndex + 1) % MODES.length];
  setColorMode(nextMode);
};
</script>

<template>
  <Button
    variant="ghost"
    size="icon"
    @click="cycleTheme"
  >
    <component
      :is="ICONS[darkMode]"
      class="size-5"
    />
  </Button>
</template>
