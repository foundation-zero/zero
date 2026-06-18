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
import PumpInstance from "../instances/PumpInstance.vue";
import { ControlValue, SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";
import ManualControl from "./partials/ManualControl.vue";
import TemperatureController from "./partials/TemperatureController.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.Pump>>();

const { labels, actions, items, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <PumpInstance v-bind="props" />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValue
        :source="controls.pump"
        field="dutypoint"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("relativeDutyPoint") }}
            <FieldRenderer.Source external>{{
              sources("pumpFlowController")
            }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Percentage />
          </TooltipListItemValue>
        </TooltipListItem>
      </ControlValue>
      <ControlValue
        :source="controls.pump"
        field="on"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("onOff") }}
            <FieldRenderer.Source external>
              {{ sources("pumpFlowController") }}
            </FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.OnOff />
          </TooltipListItemValue>
        </TooltipListItem>
      </ControlValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="sensors.pressure"
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
      <SensorValue
        :source="sensors.pump"
        field="flow"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("flow") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.FlowRate />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("energyConsumption") }}
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.Energy :value="600" />
        </TooltipListItemValue>
      </TooltipListItem>
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("powerInput") }}
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.Power :value="200" />
        </TooltipListItemValue>
      </TooltipListItem>
      <SensorValue
        :source="sensors.pump"
        field="speed"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("speed") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Frequency />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.pump"
        field="opTime"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("operationTime") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.TimeRemaining />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("totalRunningHours") }}
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.TimeRemaining :value="25 * 60 + 31" />
        </TooltipListItemValue>
      </TooltipListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ actions("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <FlowController
        :controller="controls.flowController"
        :measurement="sensors.flowMeasurement"
        :setpoint="parameters.flow"
      >
        {{ sources("pumpFlowController") }}
      </FlowController>
      <TemperatureController
        :controller="controls.temperatureController"
        :measurement="sensors.temperatureMeasurement"
        :setpoint="parameters.temperature"
      >
        {{ sources("pumpTemperatureController") }}
      </TemperatureController>
    </TooltipList>
  </MimicTooltip>
</template>
