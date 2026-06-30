<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ManualModeToggleDialog } from "@/modules/thrapp/components/manual-mode-toggle";
import { getTooltipContext, TooltipContent } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { useAutomaticMode } from "@/modules/thrapp/state";
import { useTranslations } from "..";

const { t, items, actions } = useTranslations();

const { setDialog } = getTooltipContext();

const automaticMode = useAutomaticMode();

defineProps<{ tooltip?: TooltipContent }>();

const enableAutomaticControl = async () => {
  automaticMode.value = true;
};
</script>

<template>
  <TooltipListItem class="mt-3">
    <template v-if="automaticMode">
      <TooltipListItemTitle class="text-muted-foreground text-xs">
        {{ items("automatedControl") }}
      </TooltipListItemTitle>
      <Button
        size="sm"
        @click="setDialog(ManualModeToggleDialog)"
      >
        {{ actions("controlManually") }}
      </Button>
    </template>
    <template v-else>
      <TooltipListItemTitle class="text-warning text-xs">
        {{ t("thrapp.dialogs.manualMode.warning") }}
      </TooltipListItemTitle>
      <Button
        size="sm"
        @click="enableAutomaticControl"
      >
        {{ actions("controlAutomatically") }}
      </Button>
    </template>
  </TooltipListItem>
</template>
