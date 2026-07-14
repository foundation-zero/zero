<script setup lang="ts">
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list/index.ts";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import HVACInstance from "../instances/HVACInstance.vue";
import { SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import Circuit from "./partials/Circuit.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";

const { items, labels, sources } = useTranslations();

const props = defineProps<TooltipComponentContext<MimicComponentType.HVAC>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <HVACInstance
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
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="heat"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("heatExchange") }}
            <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Heat />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="deltaT"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("deltaTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.DeltaT />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <Circuit :sensors="sensors" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("controls") }}</TooltipListHeader>
      <FlowController
        :controller="controllerState.controller"
        :setpoint="parameters.flow"
        :measurement="sensors.flow"
      />
    </TooltipList>
  </MimicTooltip>
</template>
