import { DEFINITIONS } from "@/modules/thrsim/lib/consts";
import { useAutomationStore } from "@/modules/thrsim/stores/automation";
import { computed, inject, Ref, toRefs } from "vue";

export const useAutomaticMode = () => {
  const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
  const { control } = toRefs(useAutomationStore());
  const { setAutomatedControl } = useAutomationStore();

  return computed({
    get() {
      return control.value?.modules?.[currentDefinition.value as keyof typeof control.value.modules]
        ?.controlMode?.automatic;
    },
    set(value: boolean) {
      setAutomatedControl(currentDefinition.value)(value);
    },
  });
};
