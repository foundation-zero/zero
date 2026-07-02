<script setup lang="ts">
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
} from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import LoopCircuitInstance from "../instances/LoopCircuitInstance.vue";
import { SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import Circuit from "./partials/Circuit.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.ExchangeCircuit>>();

const { labels, items, actions } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <LoopCircuitInstance
        v-bind="props"
        force-height
      />
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
