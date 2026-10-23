<script setup lang="ts">
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { SensorGraph } from "../components/sensor-graph";
import { PropulsionCoolerInstance } from "../instances";
import * as Partials from "./partials";
import Circuit from "./partials/ExchangeCircuitPartial.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.PropulsionCooler>>();

const { labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PropulsionCoolerInstance v-bind="props" />
      </NoopTooltipProvider>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <SensorGraph
        :device="tooltip?.technicalName"
        type="heat_transfers"
        :field="['heat', 'flow', 'delta_t']"
      />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("heatExchange") }}
      </TooltipListHeader>
      <Circuit :source="source" />
    </TooltipList>
  </MimicTooltip>
</template>
