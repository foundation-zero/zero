<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { ResponsivePopup } from "@/modules/common/components/responsive-dialog";
import { tScoped } from "@/modules/common/lib/utils";
import { ManualModeToggleDialog } from "@/modules/thrapp/components/manual-mode-toggle";
import { ModeBadgeSize, ModeBadges } from "@/modules/thrapp/mimics/components/mode-badge";
import { useAdvisoryEnabled, useAutomaticMode } from "@/modules/thrapp/state";
import { useAutomationStore } from "@/modules/thrsim/stores/automation";
import { ENV } from "@/settings";
import { RiLock2Fill } from "@remixicon/vue";
import { ref, toRefs } from "vue";
import { ThrsModules } from "../lib/consts";
import AdvisoryModeTooltip from "./AdvisoryModeTooltip.vue";

defineProps<{
  activeModule: keyof ThrsModules;
  modules?: string[];
}>();

const t = tScoped("thrs.components.controlActions");

const { isProcessing } = toRefs(useAutomationStore());

const isAutomatic = useAutomaticMode();
const advisoryEnabled = useAdvisoryEnabled();

const shouldShowManualModeDialog = !!ENV.VITE_MANUAL_MODE_PWD;
const showManualModeDialog = ref(false);

const toggleAutomaticMode = async () => {
  if (isAutomatic.value && shouldShowManualModeDialog) {
    showManualModeDialog.value = true;
  } else {
    isAutomatic.value = !isAutomatic.value;
  }
};
</script>

<template>
  <AdvisoryModeTooltip v-if="!advisoryEnabled" />

  <template v-else>
    <div
      class="flex cursor-pointer items-center gap-2"
      @click="toggleAutomaticMode"
    >
      <span
        class="text-sm"
        :class="{ 'text-warning': !isAutomatic }"
      >
        {{ isAutomatic ? t("automatedControl") : t("manualControl") }}
      </span>
      <Switch
        :model-value="isAutomatic || showManualModeDialog"
        :disabled="isProcessing"
        class="data-[state=unchecked]:*:data-[slot=switch-thumb]:bg-warning! data-[state=unchecked]:border-warning relative w-9 data-[state=checked]:*:data-[slot=switch-thumb]:translate-x-[calc(100%+8px)]"
      >
        <template #default>
          <RiLock2Fill
            class="text-brand absolute left-1 size-3"
            :class="{ 'opacity-0': !isAutomatic }"
          />
        </template>
      </Switch>

      <ModeBadges
        v-if="isAutomatic"
        :module="activeModule"
        :size="ModeBadgeSize.Circuit"
      />
    </div>

    <ResponsivePopup
      v-model:open="showManualModeDialog"
      class="bg-background px-0 pb-0 max-md:px-4"
    >
      <ManualModeToggleDialog @close="showManualModeDialog = false" />
    </ResponsivePopup>
  </template>
</template>
