<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { tScoped } from "@/modules/common/lib/utils";
import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";

const tLabels = tScoped("thrapp.tooltips.labels");
const tItems = tScoped("thrapp.tooltips.items");
defineProps<{ tooltip?: TooltipContent }>();
</script>

<template>
  <TooltipListItem class="mt-3">
    <TooltipListItemTitle class="text-muted-foreground text-xs">
      {{ tItems("automatedControl") }}
    </TooltipListItemTitle>
    <Button size="sm">{{ tLabels("controlManually") }}</Button>
  </TooltipListItem>
</template>
