<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ManualModeToggleDialog } from "@/modules/thrapp/components/manual-mode-toggle";
import { getTooltipContext } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { useAdvisoryEnabled, useAutomaticMode } from "@/modules/thrapp/state";
import { ENV } from "@/settings";
import { RiCpuLine, RiSteering2Line } from "@remixicon/vue";
import { useTranslations } from "..";

const { t, items, actions } = useTranslations();

const { setDialog } = getTooltipContext();

const shouldShowManualModeDialog = !!ENV.VITE_MANUAL_MODE_PWD;
const automaticMode = useAutomaticMode();
const advisoryEnabled = useAdvisoryEnabled();

const enableAutomaticControl = async () => {
  automaticMode.value = true;
};

const toggleMode = async () => {
  if (shouldShowManualModeDialog) {
    setDialog(ManualModeToggleDialog);
  } else {
    automaticMode.value = false;
  }
};
</script>

<template>
  <TooltipListItem class="mt-3">
    <template v-if="!advisoryEnabled">
      <TooltipListItemTitle class="text-destructive">
        {{ t("thrapp.dialogs.manualMode.advisoryDisabled") }}
      </TooltipListItemTitle>
    </template>
    <template v-else-if="automaticMode">
      <TooltipListItemTitle class="text-muted-foreground">
        {{ items("automatedControl") }}
      </TooltipListItemTitle>
      <Button
        size="sm"
        @click="toggleMode"
      >
        <RiSteering2Line />
        {{ actions("controlManually") }}
      </Button>
    </template>
    <template v-else>
      <TooltipListItemTitle class="text-warning">
        {{ t("thrapp.dialogs.manualMode.warning") }}
      </TooltipListItemTitle>
      <Button
        size="sm"
        @click="enableAutomaticControl"
      >
        <RiCpuLine />
        {{ actions("controlAutomatically") }}
      </Button>
    </template>
  </TooltipListItem>
</template>
