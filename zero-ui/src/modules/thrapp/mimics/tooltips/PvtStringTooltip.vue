<script setup lang="ts">
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { PvtStringInstance } from "../instances";
import * as Partials from "./partials";
import Circuit from "./partials/ExchangeCircuitPartial.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.PvtString>>();
const { labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PvtStringInstance v-bind="props" />
      </NoopTooltipProvider>
    </div>
    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>
    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <Circuit :source="source" />
    </TooltipList>
  </MimicTooltip>
</template>
