import { Breakpoints } from "@/@types";
import {
  useBreakpoints,
  breakpointsTailwind,
  useScroll,
  useWindowSize,
  useScreenOrientation,
} from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";

const twBreakpoints = useBreakpoints(breakpointsTailwind);
const orientation = useScreenOrientation();
const isMobile = () => window.navigator.userAgent.toLowerCase().includes("mobi");

export const useUIStore = defineStore("UI", () => {
  const scroll = useScroll(window);

  const isScrolling = computed(() => scroll.y.value > 45);
  const isBottom = ref(false);
  const hasScroll = ref(false);
  const breakpoints = computed<Breakpoints>(() => ({
    mobile: isMobile(),
    phone:
      twBreakpoints.smaller("md").value ||
      (twBreakpoints.between("md", "lg").value &&
        !!orientation.orientation.value?.includes("landscape")),

    tablet: twBreakpoints.between("md", "lg").value,
    desktop: twBreakpoints.greaterOrEqual("lg").value,
    landscape: !!orientation.orientation.value?.includes("landscape"),
    portrait: !!orientation.orientation.value?.includes("portrait"),
  }));

  watch(
    [scroll.y, useWindowSize().height, useRoute()],
    () => {
      hasScroll.value = document.body.scrollHeight > window.innerHeight;
      isBottom.value = scroll.arrivedState.bottom;
    },
    { immediate: true },
  );

  return { scroll, isScrolling, hasScroll, isBottom, breakpoints };
});
