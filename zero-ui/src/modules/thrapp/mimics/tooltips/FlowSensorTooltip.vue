<script setup lang="ts">
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import { FlowSensorInstance } from "../instances";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.FlowSensor>>();

const { items, labels, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <FlowSensorInstance v-bind="props" />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="sensors.flow"
        field="flow"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("flow") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.FlowRate />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <!-- // TODO: what's this? -->
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("quantity") }}
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.QuantityLiters :value="10" />
        </TooltipListItemValue>
      </TooltipListItem>
      <SensorValue
        :source="sensors.flow"
        field="temperature"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("temperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <FlowController
        :controller="controls.controller"
        :measurement="sensors.flow"
        :setpoint="parameters.flow"
      >
        <template #actuator>
          <FieldRenderer.Source :source="controls.pump" />
        </template>
        <template #measurement>
          <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
        </template>
      </FlowController>
    </TooltipList>
  </MimicTooltip>
</template>
