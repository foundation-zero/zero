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
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import TemperatureSensorInstance from "../instances/TemperatureSensorInstance.vue";
import { isField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import ComponentInfo from "./partials/ComponentInfo.vue";
import TemperatureController from "./partials/TemperatureController.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.TemperatureSensor>>();

const { items, labels, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <TemperatureSensorInstance v-bind="props" />
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

    <TooltipList v-if="isField(controllerState.controller)">
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <TemperatureController
        :controller="controllerState.controller"
        :measurement="sensors.measurement"
        :setpoint="parameters.temperature"
      >
        <template #actuator>
          <FieldRenderer.Source :source="controls.pump" />
        </template>
        <template
          v-if="sensors.measurement === source"
          #measurement
        >
          <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
        </template>
      </TemperatureController>
    </TooltipList>
  </MimicTooltip>
</template>
