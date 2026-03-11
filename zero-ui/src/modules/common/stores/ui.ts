import { Breakpoints } from "@/modules/domestic/types";
import {
  BasicColorSchema,
  breakpointsTailwind,
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
import { useAuthStore } from "../../domestic/stores/auth";

const twBreakpoints = useBreakpoints(breakpointsTailwind);
const orientation = useScreenOrientation();

export const useUIStore = defineStore("UI", () => {
  const darkMode = useLocalStorage<BasicColorSchema>("dark-mode", "auto");
  const colorMode = useColorMode({
    initialValue: darkMode.value,
  });

  const auth = useAuthStore();
  const isTouchDevice = "ontouchstart" in document.documentElement;
  const scroll = useScroll(window, { behavior: "smooth" });

  const scrollPositions = ref<Record<string, number>>({});

  const isScrolling = computed(() => scroll.y.value > 45);
  const isBottom = ref(false);
  const hasScroll = ref(false);
  const breakpoints = computed<Breakpoints>(() => ({
    touch: isTouchDevice,
    phone:
      twBreakpoints.smaller("md").value ||
      (twBreakpoints.between("md", "lg").value &&
        !!orientation.orientation.value?.includes("landscape")),

    tablet: twBreakpoints.greaterOrEqual("md").value,
    desktop: twBreakpoints.greaterOrEqual("lg").value,
    landscape: !!orientation.orientation.value?.includes("landscape"),
    portrait: !!orientation.orientation.value?.includes("portrait"),
  }));

  const showSideNav = ref((!isTouchDevice || breakpoints.value.tablet) && auth.isAdmin);

  // Only show the sidenav for admins, and hide it on mobile devices
  watch(
    () => auth.isAdmin,
    (isAdmin) => {
      showSideNav.value = isAdmin && (!isTouchDevice || breakpoints.value.tablet);
    },
    { immediate: true },
  );

  const setScrollPosition = (key: string, value: number) => (scrollPositions.value[key] = value);
  const toggleNav = (val = !showSideNav.value) => {
    showSideNav.value = val || !isTouchDevice;
  };

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
    scrollPositions,
    showSideNav,
    toggleNav,
    setScrollPosition,
    darkMode,
    colorMode,
    setColorMode,
  };
});
