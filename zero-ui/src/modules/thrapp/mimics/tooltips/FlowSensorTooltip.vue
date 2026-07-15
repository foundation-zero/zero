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
import { YardTag } from "../components/yard-tag";
import { FlowSensorInstance } from "../instances";
import { isField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.FlowSensor>>();

const { items, labels, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <FlowSensorInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="flow"
      >
        <Partials.ListItem>
          {{ items("flow") }}
        </Partials.ListItem>
      </SensorValue>
      <Partials.ListItem>
        {{ items("quantity") }}
        <template #value>
          <FieldRenderer.QuantityLiters :value="10" />
        </template>
      </Partials.ListItem>
      <SensorValue
        :source="source"
        field="temperature"
      >
        <Partials.ListItem>
          {{ items("temperature") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList v-if="isField(controllerState.controller)">
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Partials.FlowController
        :controller="controllerState.controller"
        :measurement="source"
        :setpoint="parameters.flow"
      >
        <template #actuator>
          <FieldRenderer.Source :source="controls.pump" />
        </template>
        <template #measurement>
          <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
        </template>
      </Partials.FlowController>
    </TooltipList>
  </MimicTooltip>
</template>
