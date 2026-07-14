<script setup lang="ts">
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import LoopCircuitInstance from "../instances/LoopCircuitInstance.vue";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import Circuit from "./partials/Circuit.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.ExchangeCircuit>>();

const { labels, items, actions } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <LoopCircuitInstance
          v-bind="props"
          force-height
        />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("mode") }}
        <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
      </TooltipListHeader>
      <SensorValue
        :source="sensors.heatExchanger"
        field="heat"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("circuit") }}
          </TooltipListItemTitle>
          <FieldRenderer.HeatExchangerMode />
        </TooltipListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ custom.circuitName }}
        <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Circuit :sensors="sensors" />
    </TooltipList>
  </MimicTooltip>
</template>
