import { useScroll, useWindowSize } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref, toRef, watch } from "vue";
import { useRoute } from "vue-router";

export const useUIStore = defineStore("UI", () => {
  const scroll = useScroll(window);

  const isScrolling = computed(() => scroll.y.value > 45);
  const isBottom = ref(false);
  const hasScroll = ref(false);

  watch(
    [scroll.y, useWindowSize().height, useRoute()],
    () => {
      hasScroll.value = document.body.scrollHeight > window.innerHeight;
      isBottom.value = scroll.arrivedState.bottom;
    },
    { immediate: true },
  );

  return { scroll, isScrolling, hasScroll, isBottom };
});
