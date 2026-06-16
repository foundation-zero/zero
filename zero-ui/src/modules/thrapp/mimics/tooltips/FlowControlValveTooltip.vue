<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItemAction,
} from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import FlowControlValveInstance from "../instances/FlowControlValveInstance.vue";
import { ControlValue } from "../providers";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import ComponentInfo from "./partials/ComponentInfo.vue";
import ManualControl from "./partials/ManualControl.vue";
import TemperatureController from "./partials/TemperatureController.vue";
import ValvePosition from "./partials/ValvePosition.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.FlowControlValve>>();

const { labels, items } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <FlowControlValveInstance v-bind="props" />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValue
        :source="controls.valve"
        field="setpoint"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("setpoint") }}
            <FieldRenderer.Source external>{{ custom.controllerName }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Percentage />
          </TooltipListItemValue>
        </TooltipListItem>
      </ControlValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <ValvePosition :valve="sensors.valve" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <TemperatureController
        :controller="controls.controller"
        :measurement="sensors.measurement"
        :setpoint-name="custom.setpointName"
      >
        <FieldRenderer.Source external>{{ custom.controllerName }}</FieldRenderer.Source>
      </TemperatureController>
    </TooltipList>
  </MimicTooltip>
</template>
