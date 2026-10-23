<script setup lang="ts">
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { SensorGraph } from "../components/sensor-graph";
import { PropulsionDriveInstance } from "../instances";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
import Circuit from "./partials/ExchangeCircuitPartial.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.PropulsionDrive>>();

const { labels, items } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PropulsionDriveInstance v-bind="props" />
      </NoopTooltipProvider>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <SensorGraph
        :device="tooltip?.technicalName ? `${tooltip.technicalName}-heat` : undefined"
        type="heat_transfers"
        :field="['heat', 'flow', 'delta_t']"
      />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("heatExchange") }}
      </TooltipListHeader>
      <Circuit :source="sensors.heatTransfer" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        v-if="source"
        :source="source"
        field="active"
      >
        <Partials.ListItem no-source>
          {{ items("state") }}
          <template #value>
            <FieldRenderer.HeatPumpMode />
          </template>
        </Partials.ListItem>
      </SensorValue>

      <SensorValue
        :source="source"
        field="power"
      >
        <Partials.ListItem no-source>
          {{ items("power") }}
          <template #value>
            <FieldRenderer.Power />
          </template>
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="tempPowerStage"
      >
        <Partials.ListItem no-source>
          {{ items("internalTemperature") }}
          <template #value>
            <FieldRenderer.Temperature />
          </template>
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
