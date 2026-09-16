<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItemAction,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import ExchangeCircuit from "../instances/components/ExchangeCircuit.vue";
import { ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
import Circuit from "./partials/Circuit.vue";
const props = defineProps<TooltipComponentContext<MimicComponentType.ExchangeCircuit>>();

const { labels, items, actions } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <ExchangeCircuit
        class="w-49"
        v-bind="props"
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
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
        <Partials.ListItem>
          {{ items("circuit") }}
          <template #value>
            <FieldRenderer.HeatExchangerMode />
          </template>
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ custom.circuitName }}
        <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Circuit
        :incoming="sensors.incoming"
        :outgoing="sensors.outgoing"
        :delta-t="sensors.deltaT as ModuleField<SensorComponentType.DeltaT>"
        :flow="sensors.flow"
      />
    </TooltipList>
  </MimicTooltip>
</template>
