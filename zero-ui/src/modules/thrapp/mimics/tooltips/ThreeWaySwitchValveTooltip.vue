<script setup lang="ts">
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import { FieldEditor } from "../editors";
import ThreeWaySwitchValveInstance from "../instances/ThreeWaySwitchValveInstance.vue";
import { ControlValueForm } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
import ComponentInfo from "./partials/ComponentInfo.vue";
import ManualControl from "./partials/ManualControl.vue";
import SubmitControlForm from "./partials/SubmitControlForm.vue";
const props = defineProps<TooltipComponentContext<MimicComponentType.ThreeWaySwitchValve>>();

const { labels, items, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <ThreeWaySwitchValveInstance v-bind="props" />
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
        <Partials.EditableListItem
          :renderer="FieldRenderer.ValveState"
          :editor="FieldEditor.OpenClosed"
        >
          {{ items("setpoint") }}
          <template #sourceName>
            {{ sources("this") }}
          </template>
        </Partials.EditableListItem>
        <SubmitControlForm />
      </ControlValueForm>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <Partials.ValvePosition :valve="source" />
    </TooltipList>
  </MimicTooltip>
</template>
