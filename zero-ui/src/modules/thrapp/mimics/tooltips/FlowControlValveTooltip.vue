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
import FlowControlValveInstance from "../instances/FlowControlValveInstance.vue";
import ControlValueForm from "../providers/ControlValueForm.vue";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.FlowControlValve>>();

const { labels, items, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <FlowControlValveInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <Partials.ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValueForm :source="controls.valve">
        <Partials.EditableListItem>
          {{ items("setpoint") }}
          <template #sourceName>
            {{ sources("this") }}
          </template>
        </Partials.EditableListItem>
        <Partials.SubmitButton />
      </ControlValueForm>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <Partials.ValvePosition :valve="source" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Partials.FlowController
        :controller="controllerState.controller"
        :measurement="sensors.measurement"
        :setpoint="parameters.flow"
      >
        <template #actuator>
          <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
        </template>
        <template #measurement>
          <FieldRenderer.Source :source="sensors.measurement" />
        </template>
      </Partials.FlowController>
    </TooltipList>
  </MimicTooltip>
</template>
