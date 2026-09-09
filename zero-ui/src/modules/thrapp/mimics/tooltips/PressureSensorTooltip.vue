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
import { SensorGraph } from "../components/sensor-graph";
import { YardTag } from "../components/yard-tag";
import PressureSensorInstance from "../instances/PressureSensorInstance.vue";
import { SensorValue } from "../providers";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.PressureSensor>>();

const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PressureSensorInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <SensorGraph
        :device="tooltip?.technicalName"
        type="pressures"
        field="pressure"
      />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="pressure"
      >
        <Partials.ListItem>
          {{ items("pressure") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList v-if="custom.controller">
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Partials.PIDController v-bind="custom.controller" />
    </TooltipList>
  </MimicTooltip>
</template>
