<script setup lang="ts" generic="K extends keyof ControlStatus['modules']">
import { Switch } from "@/components/ui/switch";
import { tScoped } from "@/modules/common/lib/utils";
import {
  ControlStatus,
  PvtAutomaticMode,
  useSimulationStore,
} from "@/modules/thrs/stores/simulation";
import { computed, toRefs } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
  module: string;
}>();

const t = tScoped("thrs.components.controlActions");
const { te } = useI18n();

const { control, isProcessing } = toRefs(useSimulationStore());
const simulationStore = useSimulationStore();
const setAutomatedControl = simulationStore.setAutomatedControl(props.module);

const isAutomated = computed(
  () => !!control.value?.modules?.[props.module as K]?.controlMode?.automatic,
);

const mode = computed(() => {
  const automaticMode = control.value?.modules?.[props.module as K]?.controlMode?.automaticMode;

  if (!automaticMode || !te(`modes.${props.module}`)) {
    return undefined;
  } else if (props.module === "pvt") {
    const pvtMode = automaticMode as PvtAutomaticMode;

    return t("modes.pvt", {
      aftMode: pvtMode.aft.mode,
      fwdMode: pvtMode.fwd.mode,
      ownersMode: pvtMode.owners.mode,
    });
  } else {
    return t(`modes.${props.module}`, automaticMode);
  }
});
</script>

<template>
  <div
    class="flex cursor-pointer items-center gap-4"
    @click="setAutomatedControl(!isAutomated)"
  >
    <span class="flex flex-col items-end text-sm">
      {{ t("automatedControl") }}
      <span class="text-muted-foreground text-xs font-light uppercase">
        {{ isAutomated ? mode : t("off") }}
      </span>
    </span>
    <Switch
      :model-value="isAutomated"
      :disabled="isProcessing"
    />
  </div>
</template>
