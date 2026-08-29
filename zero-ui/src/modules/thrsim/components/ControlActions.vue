<script setup lang="ts" generic="K extends keyof ControlStatus['modules']">
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import InfoTooltip from "@/modules/common/components/info-tooltip/InfoTooltip.vue";
import { ResponsivePopup } from "@/modules/common/components/responsive-dialog";
import { tScoped } from "@/modules/common/lib/utils";
import { ManualModeToggleDialog } from "@/modules/thrapp/components/manual-mode-toggle";
import { useAdvisoryEnabled, useAutomaticMode } from "@/modules/thrapp/state";
import {
  ControlStatus,
  DhwAutomaticMode,
  PvtAutomaticMode,
  ThrustersAutomaticMode,
  useAutomationStore,
} from "@/modules/thrsim/stores/automation";
import { ENV } from "@/settings";
import { RiLock2Fill } from "@remixicon/vue";
import { computed, ref, toRefs } from "vue";

const props = defineProps<{
  activeModule: string;
  modules?: string[];
}>();

const t = tScoped("thrs.components.controlActions");

const { control, isProcessing } = toRefs(useAutomationStore());

const isAutomatic = useAutomaticMode();
const advisoryEnabled = useAdvisoryEnabled();

const modes = computed(() => {
  const automaticMode =
    control.value?.modules?.[props.activeModule as K]?.controlMode?.automaticMode;

  if (!automaticMode) {
    return undefined;
  } else if (props.activeModule === "pvt") {
    const pvtMode = automaticMode as PvtAutomaticMode;

    return [
      t(`modes.pvt.${pvtMode.aft.mode}`, { count: 0 }),
      t(`modes.pvt.${pvtMode.fwd.mode}`, {
        count: 1,
      }),
      t(`modes.pvt.${pvtMode.owners.mode}`, {
        count: 2,
      }),
    ];
  } else if (props.activeModule === "dhw") {
    const dhwMode = automaticMode as DhwAutomaticMode;

    return [t(`modes.dhw.${dhwMode.boostingMode}`)];
  } else if (props.activeModule === "thrusters") {
    const thrustersMode = automaticMode as ThrustersAutomaticMode;

    return [t(`modes.thrusters.${thrustersMode.mode}`)];
  } else {
    return [t(`modes.${props.activeModule}`, automaticMode)];
  }
});

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
  <div
    v-if="!advisoryEnabled"
    class="text-destructive flex justify-center text-sm"
  >
    {{ t("advisoryDisabled") }}
    <div class="ml-1">
      <InfoTooltip class="stroke-destructive fill-destructive text-destructive">
        {{ t("advisoryDisabledTooltip") }}
      </InfoTooltip>
    </div>
  </div>

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

      <Badge
        v-for="mode in modes"
        :key="mode"
        class="bg-heating-medium"
      >
        {{ mode }}
      </Badge>
    </div>

    <ResponsivePopup
      v-model:open="showManualModeDialog"
      class="bg-background px-0 pb-0 max-md:px-4"
    >
      <ManualModeToggleDialog @close="showManualModeDialog = false" />
    </ResponsivePopup>
  </template>
</template>
