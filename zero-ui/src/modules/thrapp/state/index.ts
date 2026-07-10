import { DEFINITIONS } from "@/modules/thrs/lib/consts";
import { useSimulationStore } from "@/modules/thrs/stores/simulation";
import { computed, inject, Ref, toRefs } from "vue";

export const useAutomaticMode = () => {
  const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
  const { control } = toRefs(useSimulationStore());
  const { setAutomatedControl } = useSimulationStore();

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
