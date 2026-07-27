<script setup lang="ts">
import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { useTranslations } from "..";

const { items } = useTranslations();

defineProps<{ tooltip?: TooltipContent }>();
</script>

<template>
  <TooltipListItem
    v-if="tooltip?.technicalName"
    size="sm"
  >
    <TooltipListItemTitle>{{ items("technicalName") }}</TooltipListItemTitle>
    <TooltipListItemTitle>{{ tooltip.technicalName }}</TooltipListItemTitle>
  </TooltipListItem>
  <TooltipListItem
    v-if="tooltip?.mqttTopic"
    size="sm"
  >
    <TooltipListItemTitle>{{ items("mqttTopic") }}</TooltipListItemTitle>
    <TooltipListItemTitle>{{ tooltip.mqttTopic }}</TooltipListItemTitle>
  </TooltipListItem>
  <TooltipListItem
    v-if="tooltip?.componentType"
    size="sm"
  >
    <TooltipListItemTitle>{{ items("componentType") }}</TooltipListItemTitle>
    <TooltipListItemTitle>{{ tooltip.componentType }}</TooltipListItemTitle>
  </TooltipListItem>
</template>
