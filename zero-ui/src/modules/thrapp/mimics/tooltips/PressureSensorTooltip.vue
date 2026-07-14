<script setup lang="ts">
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import PressureSensorInstance from "../instances/PressureSensorInstance.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

import { useTranslations } from ".";
import {
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import FlowController from "./partials/FlowController.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.PressureSensor>>();

const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PressureSensorInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="pressure"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("pressure") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Pressure />
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
        :controller="controllerState.controller"
        :measurement="sensors.flow"
        :setpoint="parameters.flow"
      >
        <template #actuator>
          <FieldRenderer.Source :source="controls.pump" />
        </template>
      </FlowController>
    </TooltipList>
  </MimicTooltip>
</template>
