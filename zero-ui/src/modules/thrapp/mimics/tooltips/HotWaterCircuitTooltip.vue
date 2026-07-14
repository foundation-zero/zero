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
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import HotWaterCircuitInstance from "../instances/HotWaterCircuitInstance.vue";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.HotWaterCircuit>>();

const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <HotWaterCircuitInstance
          v-bind="props"
          height="243"
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
        {{ labels("exchangeCircuit") }}
      </TooltipListHeader>
      <SensorValue
        :source="sensors.tIn"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("incomingTemperature") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.flowIn"
        field="flow"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("incomingFlow") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.FlowRate />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.tOut"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("outgoingTemperature") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.flowOut"
        field="flow"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("outgoingFlow") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.FlowRate />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
