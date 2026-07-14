<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
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
import { FieldEditor } from "../editors";
import FlowControlValveInstance from "../instances/FlowControlValveInstance.vue";
import { ControlValue } from "../providers";
import ControlValueForm from "../providers/ControlValueForm.vue";
import { FieldRenderer } from "../renderers";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";
import ManualControl from "./partials/ManualControl.vue";
import SubmitControlForm from "./partials/SubmitControlForm.vue";
import ValvePosition from "./partials/ValvePosition.vue";

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
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValueForm :source="controls.valve">
        <ControlValue
          :source="controls.valve"
          field="setpoint"
        >
          <TooltipListItem>
            <TooltipListItemTitle>
              {{ items("setpoint") }}
              <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
            </TooltipListItemTitle>
            <FieldEditor.Auto>
              <TooltipListItemValue>
                <FieldRenderer.Auto />
              </TooltipListItemValue>
            </FieldEditor.Auto>
          </TooltipListItem>
        </ControlValue>
        <SubmitControlForm />
      </ControlValueForm>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <ValvePosition :valve="source" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <FlowController
        :controller="controllerState.controller"
        :measurement="sensors.measurement"
        :actuator="controls.pump"
        :setpoint="parameters.flow"
      >
        <template #actuator>
          <FieldRenderer.Source :source="controls.pump" />
        </template>
      </FlowController>
    </TooltipList>
  </MimicTooltip>
</template>
