import { useScroll } from "@vueuse/core";
import { computed, Ref } from "vue";

export { default as TopNav } from "./TopNav.vue";
export { default as TopNavToolbar } from "./TopNavToolbar.vue";

export const useScrollOffset = (elementToHide: Ref<HTMLElement | null>) => {
  const { y } = useScroll(window);

  return computed(() => `-${Math.min(y.value, elementToHide.value?.clientHeight ?? 0)}px`);
};
