<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { useSimulationStore } from "@/modules/thrs/stores/simulation";
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

const mode = computed(
  () => control.value?.modules?.[props.module]?.controlMode?.automaticMode?.mode,
);
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
