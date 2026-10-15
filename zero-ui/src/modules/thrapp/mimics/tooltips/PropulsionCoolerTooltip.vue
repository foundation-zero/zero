<script setup lang="ts">
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list/index.ts";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { SensorGraph } from "../components/sensor-graph/index.ts";
import { PropulsionCoolerInstance } from "../instances";
import { useTranslations } from "./index.ts";
import Circuit from "./partials/ExchangeCircuitPartial.vue";
import * as Partials from "./partials/index.ts";

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
        field="heat"
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
