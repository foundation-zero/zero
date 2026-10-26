<script setup lang="ts">
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { PvtStringInstance } from "../instances";
import { SensorValue } from "../providers";
import * as Partials from "./partials";

const props = defineProps<TooltipComponentContext<MimicComponentType.PvtString>>();
const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PvtStringInstance v-bind="props" />
      </NoopTooltipProvider>
    </div>
    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>
    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="sensors.flow"
        field="flow"
      >
        <Partials.ListItem>
          {{ items("flow") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.supplyTemperature"
        field="temperature"
      >
        <Partials.ListItem>
          {{ items("incomingTemperature") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.returnTemperature"
        field="temperature"
      >
        <Partials.ListItem>
          {{ items("outgoingTemperature") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
