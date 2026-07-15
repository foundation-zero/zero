<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ManualModeToggleDialog } from "@/modules/thrapp/components/manual-mode-toggle";
import { getTooltipContext } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { useAutomaticMode } from "@/modules/thrapp/state";
import { RiCpuLine, RiSteering2Line } from "@remixicon/vue";
import { useTranslations } from "..";

const { t, items, actions } = useTranslations();

const { setDialog } = getTooltipContext();

const automaticMode = useAutomaticMode();

const enableAutomaticControl = async () => {
  automaticMode.value = true;
};
</script>

<template>
  <TooltipListItem class="mt-3">
    <template v-if="automaticMode">
      <TooltipListItemTitle class="text-muted-foreground">
        {{ items("automatedControl") }}
      </TooltipListItemTitle>
      <Button
        size="sm"
        @click="setDialog(ManualModeToggleDialog)"
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
