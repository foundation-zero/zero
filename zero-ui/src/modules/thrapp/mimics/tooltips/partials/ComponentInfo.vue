<script setup lang="ts">
import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { useTranslations } from "..";

const { items } = useTranslations();

defineProps<{ tooltip?: TooltipContent }>();
</script>

<template>
  <TooltipListItem
    v-if="tooltip?.itemName"
    size="sm"
  >
    <TooltipListItemTitle>{{ items("itemName") }}</TooltipListItemTitle>
    <TooltipListItemTitle>{{ tooltip.itemName }}</TooltipListItemTitle>
  </TooltipListItem>
  <TooltipListItem
    v-if="tooltip?.technicalName"
    size="sm"
  >
    <TooltipListItemTitle>{{ items("technicalName") }}</TooltipListItemTitle>
    <TooltipListItemTitle>{{ tooltip.technicalName }}</TooltipListItemTitle>
  </TooltipListItem>
</template>
