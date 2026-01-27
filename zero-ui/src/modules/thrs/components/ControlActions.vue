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

const isAutomated = computed(() => !!control.value?.modules?.[props.module].automatic);
</script>

<template>
  <div
    class="flex cursor-pointer items-center gap-4"
    @click="setAutomatedControl(!isAutomated)"
  >
    <Switch
      :model-value="isAutomated"
      :disabled="isProcessing"
    />
    <span>{{ t("thrs.components.controlActions.automatedControl") }}</span>
  </div>
</template>
