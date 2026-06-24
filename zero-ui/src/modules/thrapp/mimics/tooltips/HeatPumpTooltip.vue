<script setup lang="ts">
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import HeatPumpInstance from "../instances/HeatPumpInstance.vue";
import { ControlValue, SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { useTranslations } from "./index.ts";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";
import ManualControl from "./partials/ManualControl.vue";

const { items, labels, sources } = useTranslations();

const props = defineProps<TooltipComponentContext<MimicComponentType.HeatPump>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <HeatPumpInstance
        v-bind="props"
        force-height
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValue
        :source="controls.heatpump"
        field="on"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("onOff") }}
            <FieldRenderer.Source external> </FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.OnOff />
          </TooltipListItemValue>
        </TooltipListItem>
      </ControlValue>
      <ControlValue
        :source="controls.heatpump"
        field="temperatureSetpoint"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("temperature") }}
            <FieldRenderer.Source url />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </ControlValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="heat"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("heatExchange") }}
            <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Heat />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="deltaT"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("deltaTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.DeltaT />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.incoming"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("incomingTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.outgoing"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("outgoingTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("controls") }}</TooltipListHeader>
      <FlowController
        :controller="controls.controller"
        :setpoint="parameters.flow"
        :measurement="sensors.measurement"
      />
    </TooltipList>
  </MimicTooltip>
</template>
