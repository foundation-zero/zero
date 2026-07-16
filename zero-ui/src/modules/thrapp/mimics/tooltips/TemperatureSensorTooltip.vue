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
import TemperatureSensorInstance from "../instances/TemperatureSensorInstance.vue";
import { SensorValue } from "../providers";
import * as Partials from "./partials";

const props = defineProps<TooltipComponentContext<MimicComponentType.TemperatureSensor>>();

const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <TemperatureSensorInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="temperature"
      >
        <Partials.ListItem no-source>
          {{ items("temperature") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList v-if="custom.controller">
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Partials.PIDController
        v-if="custom.controller"
        v-bind="custom.controller"
      />
    </TooltipList>
  </MimicTooltip>
</template>
