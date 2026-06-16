<script setup lang="ts">
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
} from "../../components/tooltip-list/index.ts";
import TooltipListItemValue from "../../components/tooltip-list/TooltipListItemValue.vue";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { ComponentOrientation } from "../components/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import { HeatExchangerInstance } from "../instances/index.ts";
import { SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import Circuit from "./partials/Circuit.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.HeatExchanger>>();

const { labels, actions, items, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <HeatExchangerInstance
        v-bind="props"
        :orientation="ComponentOrientation.Down"
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <SensorValue
      :source="sensors.heatExchanger"
      field="heat"
    >
      <TooltipList>
        <TooltipListHeader>
          {{ labels("mode") }}
          <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
        </TooltipListHeader>
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("exchanger") }}
          </TooltipListItemTitle>
          <FieldRenderer.HeatExchangerMode />
        </TooltipListItem>
      </TooltipList>

      <TooltipList>
        <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>

        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("heatExchange") }}
            <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Heat />
          </TooltipListItemValue>
        </TooltipListItem>
      </TooltipList>
    </SensorValue>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("thisCircuit") }}
      </TooltipListHeader>
      <Circuit :sensors="custom.circuit" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("exchangeCircuit") }}
        <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Circuit :sensors="custom.exchangeCircuit" />
    </TooltipList>
  </MimicTooltip>
</template>
