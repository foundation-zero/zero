<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { BasicColorSchema, useColorMode, useLocalStorage } from "@vueuse/core";
import { Moon, Sun, SunMoon } from "lucide-vue-next";
import { FunctionalComponent } from "vue";

const darkMode = useLocalStorage<BasicColorSchema>("dark-mode", "auto");
const colorMode = useColorMode({
  initialValue: darkMode.value,
});

const MODES = ["light", "auto", "dark"] as const;

const ICONS: Record<BasicColorSchema, FunctionalComponent> = {
  light: Sun,
  dark: Moon,
  auto: SunMoon,
};

const cycleTheme = () => {
  const currentIndex = MODES.indexOf(darkMode.value);
  const nextMode = MODES[(currentIndex + 1) % MODES.length];
  colorMode.value = nextMode;
  darkMode.value = nextMode;
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
      class="size-4"
    />
  </Button>
</template>
