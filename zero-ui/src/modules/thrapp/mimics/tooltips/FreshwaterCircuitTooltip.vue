<script setup lang="ts">
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import FreshwaterCircuitContent from "../instances/content/FreshwaterCircuitContent.vue";
import { SensorValue } from "../providers";
import * as Partials from "./partials";

const props = defineProps<TooltipComponentContext<MimicComponentType.FreshwaterCircuit>>();

const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <FreshwaterCircuitContent
        v-bind="props"
        class="w-49"
      />
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
        :source="sensors.tIn"
        field="temperature"
      >
        <Partials.ListItem size="sm">
          {{ items("incomingTemperature") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.flowIn"
        field="flow"
      >
        <Partials.ListItem size="sm">
          {{ items("incomingFlow") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.tOut"
        field="temperature"
      >
        <Partials.ListItem size="sm">
          {{ items("outgoingTemperature") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.flowOut"
        field="flow"
      >
        <Partials.ListItem size="sm">
          {{ items("outgoingFlow") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
