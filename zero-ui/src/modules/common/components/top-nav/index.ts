import { useScroll } from "@vueuse/core";
import { ComponentPublicInstance, computed, Ref } from "vue";

export { default as TopNav } from "./TopNav.vue";
export { default as TopNavToolbar } from "./TopNavToolbar.vue";

export const useScrollOffset = (
  elementToHide: Ref<HTMLElement | ComponentPublicInstance | null>,
) => {
  const { y } = useScroll(window);

  return computed(() => {
    if (elementToHide.value == null) return "0px";

    const el =
      elementToHide.value instanceof HTMLElement
        ? elementToHide.value
        : (elementToHide.value.$el as HTMLElement);

    return `-${Math.min(y.value, el?.clientHeight ?? 0)}px`;
  });
};
