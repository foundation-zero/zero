<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import {
  BoilersAutomaticMode,
  PcmAutomaticMode,
  PvtAutomaticMode,
  ThrustersAutomaticMode,
  useSimulationStore,
} from "@/modules/thrs/stores/simulation";
import { computed, toRefs } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
  module: string;
}>();

const { t } = useI18n();

const { control, isProcessing } = toRefs(useSimulationStore());
const simulationStore = useSimulationStore();
const setAutomatedControl = simulationStore.setAutomatedControl(props.module);

const isAutomated = computed(
  () => !!control.value?.modules?.[props.module]?.controlMode?.automatic,
);

const mode = computed(() => {
  const automaticMode = control.value?.modules?.[props.module]?.controlMode?.automaticMode;
  if (!automaticMode) return undefined;
  if ("mode" in automaticMode)
    return (automaticMode as ThrustersAutomaticMode | PcmAutomaticMode).mode;
  if ("boostingMode" in automaticMode) {
    const m = automaticMode as BoilersAutomaticMode;
    return [`boosting: ${m.boostingMode}`, `filling: ${m.fillingMode}`].join(" / ");
  }
  if ("aft" in automaticMode) {
    const m = automaticMode as PvtAutomaticMode;
    return [`aft: ${m.aft.mode}`, `fwd: ${m.fwd.mode}`, `owners: ${m.owners.mode}`].join(" / ");
  }
  return undefined;
});
</script>

<template>
  <div
    class="flex cursor-pointer items-center gap-4"
    @click="setAutomatedControl(!isAutomated)"
  >
    <span class="flex flex-col items-end text-sm">
      {{ t("thrs.components.controlActions.automatedControl") }}
      <span class="text-muted-foreground text-xs font-light uppercase">
        {{ isAutomated ? mode : $t("thrs.components.controlActions.off") }}
      </span>
    </span>
    <Switch
      :model-value="isAutomated"
      :disabled="isProcessing"
    />
  </div>
</template>
