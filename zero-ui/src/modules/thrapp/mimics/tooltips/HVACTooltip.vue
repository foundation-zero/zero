<script setup lang="ts">
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import HVACInstance from "../instances/HVACInstance.vue";
import { ParameterValue, SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";
import ManualControl from "./partials/ManualControl.vue";

const { items, labels, sources } = useTranslations();

const props = defineProps<TooltipComponentContext<MimicComponentType.HVAC>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <HVACInstance
        v-bind="props"
        force-height
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ParameterValue :source="parameters.temperature">
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("maximumTemperature") }}
            <FieldRenderer.Source external>
              {{ sources("hvacController") }}
            </FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </ParameterValue>

      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("heatflow") }}
          <FieldRenderer.Source url>
            {{ sources("hvacHeatFlow") }}
          </FieldRenderer.Source>
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.Heat :value="200" />
        </TooltipListItemValue>
      </TooltipListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <SensorValue
        :source="sensors.heatExchanger"
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
        :source="sensors.heatExchanger"
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
      <SensorValue
        :source="sensors.incoming"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("incomingTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.outgoing"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("outgoingTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("controls") }}</TooltipListHeader>
      <FlowController
        :controller="controls.controller"
        :setpoint="parameters.flow"
        :measurement="sensors.measurement"
      />
    </TooltipList>
  </MimicTooltip>
</template>
