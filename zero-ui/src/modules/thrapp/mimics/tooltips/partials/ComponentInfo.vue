<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";

const tItems = tScoped("thrapp.tooltips.items");
defineProps<{ tooltip?: TooltipContent }>();
</script>

<template>
  <TooltipListItem
    v-if="tooltip?.itemName"
    size="sm"
  >
    <TooltipListItemTitle>{{ tItems("itemName") }}</TooltipListItemTitle>
    <TooltipListItemTitle>{{ tooltip.itemName }}</TooltipListItemTitle>
  </TooltipListItem>
  <TooltipListItem
    v-if="tooltip?.technicalName"
    size="sm"
  >
    <TooltipListItemTitle>{{ tItems("technicalName") }}</TooltipListItemTitle>
    <TooltipListItemTitle>{{ tooltip.technicalName }}</TooltipListItemTitle>
  </TooltipListItem>
</template>
