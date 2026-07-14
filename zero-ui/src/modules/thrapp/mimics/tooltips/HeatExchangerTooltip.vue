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
import TooltipListItemValue from "../../components/tooltip-list/TooltipListItemValue.vue";
import { MimicComponentType } from "../../types";
import { ComponentOrientation } from "../components";
import { YardTag } from "../components/yard-tag";
import { HeatExchangerInstance } from "../instances";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import Circuit from "./partials/Circuit.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.HeatExchanger>>();

const { labels, actions, items, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <HeatExchangerInstance
          v-bind="props"
          :orientation="ComponentOrientation.Down"
        />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <SensorValue
      :source="source"
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
      <SensorValue
        :source="source"
        field="deltaT"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("deltaTemperature") }}
            <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.DeltaT />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <Circuit :sensors="sensors" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("exchangeCircuit") }}
        <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
      </TooltipListHeader>
      <SensorValue
        :source="custom.exchangeCircuit.deltaT"
        field="deltaT"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("deltaTemperature") }}
            <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.DeltaT />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <Circuit :sensors="custom.exchangeCircuit" />
    </TooltipList>
  </MimicTooltip>
</template>
