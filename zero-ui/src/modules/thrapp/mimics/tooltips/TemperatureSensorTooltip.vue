<script setup lang="ts">
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import TemperatureSensorInstance from "../instances/TemperatureSensorInstance.vue";
import { SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import ComponentInfo from "./partials/ComponentInfo.vue";
import TemperatureController from "./partials/TemperatureController.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.TemperatureSensor>>();

const { items, labels, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <TemperatureSensorInstance v-bind="props" />
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

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <TemperatureController
        :controller="controls.controller"
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
