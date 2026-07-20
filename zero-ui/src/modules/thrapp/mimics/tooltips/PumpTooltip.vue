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
import PumpInstance from "../instances/PumpInstance.vue";
import { ControlValue, ControlValueForm, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
import ComponentInfo from "./partials/ComponentInfo.vue";
import ManualControl from "./partials/ManualControl.vue";
import SubmitControlForm from "./partials/SubmitControlForm.vue";
const props = defineProps<TooltipComponentContext<MimicComponentType.Pump>>();

const { labels, actions, items, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PumpInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValueForm :source="controls.pump">
        <ControlValue
          :source="controls.pump"
          field="dutypoint"
        >
          <Partials.EditableListItem>
            {{ items("relativeDutyPoint") }}
            <template #sourceName>
              {{ sources("this") }}
            </template>
          </Partials.EditableListItem>
        </ControlValue>
        <ControlValue
          :source="controls.pump"
          field="on"
        >
          <Partials.EditableListItem>
            {{ items("onOff") }}
            <template #sourceName>
              {{ sources("this") }}
            </template>
          </Partials.EditableListItem>
        </ControlValue>
        <SubmitControlForm />
      </ControlValueForm>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="sensors.pressure"
        field="pressure"
      >
        <Partials.ListItem no-source>
          {{ items("pressure") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="flow"
      >
        <Partials.ListItem no-source>
          {{ items("flow") }}
        </Partials.ListItem>
      </SensorValue>

      <Partials.ListItem>
        {{ items("energyConsumption") }}
        <template #renderer>
          <FieldRenderer.Energy :value="600" />
        </template>
      </Partials.ListItem>
      <Partials.ListItem>
        {{ items("powerInput") }}
        <template #renderer>
          <FieldRenderer.Power :value="200" />
        </template>
      </Partials.ListItem>
      <SensorValue
        :source="source"
        field="speed"
      >
        <Partials.ListItem no-source>
          {{ items("speed") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="opTime"
      >
        <Partials.ListItem no-source>
          {{ items("operationTime") }}
        </Partials.ListItem>
      </SensorValue>
      <Partials.ListItem>
        {{ items("totalRunningHours") }}
        <template #renderer>
          <FieldRenderer.TimeRemaining :value="25 * 60 + 31" />
        </template>
      </Partials.ListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ actions("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Partials.PIDController v-bind="custom.flowController">
        {{ sources("pumpFlowController") }}
      </Partials.PIDController>
      <Partials.PIDController v-bind="custom.temperatureController">
        {{ sources("pumpTemperatureController") }}
      </Partials.PIDController>
    </TooltipList>
  </MimicTooltip>
</template>
