<script setup lang="ts">
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list/index.ts";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import HVACInstance from "../instances/HVACInstance.vue";
import { SensorValue } from "../providers/index.ts";
import { useTranslations } from "./index.ts";
import Circuit from "./partials/Circuit.vue";

import * as Partials from "./partials/index.ts";
const { items, labels, sources } = useTranslations();

const props = defineProps<TooltipComponentContext<MimicComponentType.HVAC>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <HVACInstance
          v-bind="props"
          force-height
        />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="heat"
      >
        <Partials.ListItem no-source>
          {{ items("heatExchange") }}
          <template #sourceName>
            {{ sources("calculated") }}
          </template>
        </Partials.ListItem>
      </SensorValue>
      <Circuit
        v-bind="sensors"
        :delta-t="source"
      />
    </TooltipList>
  </MimicTooltip>
</template>
