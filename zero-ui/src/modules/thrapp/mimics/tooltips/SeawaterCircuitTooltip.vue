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
import { SeawaterCircuitInstance } from "../instances";
import { SensorValue } from "../providers";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.SeawaterCircuit>>();

const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <SeawaterCircuitInstance
          v-bind="props"
          height="243"
          force-height
        />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("connectingCircuit") }}
      </TooltipListHeader>
      <SensorValue
        :source="source"
        field="temperature"
      >
        <Partials.ListItem size="sm">
          {{ items("temperature") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
