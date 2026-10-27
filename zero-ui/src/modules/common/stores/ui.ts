import {
  BasicColorSchema,
  useBreakpoints,
  useColorMode,
  useLocalStorage,
  useScreenOrientation,
  useScroll,
  useWindowSize,
} from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { breakpointsZero } from "../lib/consts";
import { Breakpoints } from "../types";

export const BREAKPOINTS = useBreakpoints(breakpointsZero);
const orientation = useScreenOrientation();

export const useUIStore = defineStore("UI", () => {
  const darkMode = useLocalStorage<BasicColorSchema>("dark-mode", "auto");
  const colorMode = useColorMode({
    initialValue: darkMode.value,
  });

  const isTouchDevice = "ontouchstart" in document.documentElement;
  const scroll = useScroll(window, { behavior: "smooth" });

  const isScrolling = computed(() => scroll.y.value > 45);
  const isBottom = ref(false);
  const hasScroll = ref(false);
  const breakpoints = computed<Breakpoints>(() => ({
    touch: isTouchDevice,
    phone:
      BREAKPOINTS.smaller("md").value ||
      (BREAKPOINTS.between("md", "lg").value &&
        !!orientation.orientation.value?.includes("landscape")),

    tablet: BREAKPOINTS.greaterOrEqual("md").value,
    desktop: BREAKPOINTS.greaterOrEqual("lg").value,
    landscape: !!orientation.orientation.value?.includes("landscape"),
    portrait: !!orientation.orientation.value?.includes("portrait"),
  }));

  const setColorMode = (mode: BasicColorSchema) => {
    darkMode.value = mode;
    colorMode.value = mode;
  };

  watch(
    [scroll.y, useWindowSize().height, useRoute()],
    () => {
      hasScroll.value = document.body.scrollHeight > window.innerHeight;
      isBottom.value = scroll.arrivedState.bottom;
    },
    { immediate: true },
  );

  return {
    scroll,
    isScrolling,
    hasScroll,
    isBottom,
    breakpoints,
    darkMode,
    colorMode,
    setColorMode,
  };
});
