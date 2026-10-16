<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list/index.ts";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { SensorGraph } from "../components/sensor-graph/index.ts";
import { ThrusterMode } from "../components/thrusters";
import { ThrusterInstance } from "../instances/index.ts";
import { getField, SensorValue } from "../providers";
import { useTranslations } from "./index.ts";
import Circuit from "./partials/ExchangeCircuitPartial.vue";
import * as Partials from "./partials/index.ts";

const props = defineProps<TooltipComponentContext<MimicComponentType.Thruster>>();

const { labels, items } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <ThrusterInstance v-bind="props" />
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
      <Partials.ListItem no-source>
        {{ items("state") }}
        <template #value>
          <ThrusterMode :source="sensors.pcs" />
        </template>
      </Partials.ListItem>
      <SensorValue :source="getField(SensorComponentType.Thruster, 'thrusters', 'placeholder')">
        <Partials.ListItem no-source>
          {{ items("power") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue :source="getField(SensorComponentType.Temperature, 'thrusters', 'placeholder')">
        <Partials.ListItem no-source>
          {{ items("internalTemperature") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
