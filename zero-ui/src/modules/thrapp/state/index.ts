import { DEFINITIONS } from "@/modules/thrsim/lib/consts";
import { useAutomationStore } from "@/modules/thrsim/stores/automation";
import { AmcsControlMode } from "@/modules/thrsim/types";
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

export const useAdvisoryEnabled = () => {
  const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
  const { control } = toRefs(useAutomationStore());

  return computed(() => {
    const key = currentDefinition.value;
    if (!key || !control.value?.modules) return null;

    const module = control.value.modules[key as keyof typeof control.value.modules];
    if (!module?.sensorValues) return null;

    return module.sensorValues["mode"]?.mode.value === AmcsControlMode.External;
  });
};
