<script setup lang="ts">
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItemAction,
} from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import FlowControlValveInstance from "../instances/FlowControlValveInstance.vue";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";
import FlowValveSetpoint from "./partials/FlowValveSetpoint.vue";
import ManualControl from "./partials/ManualControl.vue";
import ValvePosition from "./partials/ValvePosition.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.FlowControlValve>>();

const { labels } = useTranslations();
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
      <FlowValveSetpoint :valve="controls.valve">
        <FieldRenderer.Source external>{{ custom.controllerName }}</FieldRenderer.Source>
      </FlowValveSetpoint>
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
      <FlowController
        :controller="controls.controller"
        :measurement="sensors.measurement"
      >
        <FieldRenderer.Source external>{{ custom.controllerName }}</FieldRenderer.Source>
      </FlowController>
    </TooltipList>
  </MimicTooltip>
</template>
