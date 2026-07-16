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
  TooltipListItemAction,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { ComponentOrientation } from "../components";
import { YardTag } from "../components/yard-tag";
import { HeatExchangerInstance } from "../instances";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
import Circuit from "./partials/Circuit.vue";

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
      <Partials.ComponentInfo :tooltip="tooltip" />
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
        <Partials.ListItem no-source>
          {{ items("exchanger") }}
          <template #value>
            <FieldRenderer.HeatExchangerMode />
          </template>
        </Partials.ListItem>
      </TooltipList>

      <TooltipList>
        <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
        <Partials.ListItem>
          {{ items("heatExchange") }}
          <template #sourceName>
            {{ sources("calculated") }}
          </template>
        </Partials.ListItem>
      </TooltipList>
    </SensorValue>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("thisCircuit") }}
      </TooltipListHeader>
      <Circuit
        :incoming="sensors.incoming"
        :outgoing="sensors.outgoing"
        :delta-t="source"
        :flow="sensors.flow"
      />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("exchangeCircuit") }}
        <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Circuit
        :incoming="custom.exchangeCircuit.incoming"
        :outgoing="custom.exchangeCircuit.outgoing"
        :delta-t="custom.exchangeCircuit.deltaT"
        :flow="custom.exchangeCircuit.flow"
      />
    </TooltipList>
  </MimicTooltip>
</template>
