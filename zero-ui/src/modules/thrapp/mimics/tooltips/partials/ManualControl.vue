<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { useTranslations } from "..";

const { labels, items } = useTranslations();

defineProps<{ tooltip?: TooltipContent }>();
</script>

<template>
  <TooltipListItem class="mt-3">
    <TooltipListItemTitle class="text-muted-foreground text-xs">
      {{ items("automatedControl") }}
    </TooltipListItemTitle>
    <Button size="sm">{{ labels("controlManually") }}</Button>
  </TooltipListItem>
</template>
