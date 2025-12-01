import { useScroll } from "@vueuse/core";
import { computed } from "vue";

export { default as TopNav } from "./TopNav.vue";
export { default as TopNavToolbar } from "./TopNavToolbar.vue";

export const useScrollOffset = () => {
  const { y } = useScroll(window);

  return computed(() => `-${Math.min(y.value, 64)}px`);
};
