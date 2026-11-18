<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { PowerConverterInstance } from "../instances";
import { ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";

const props = defineProps<TooltipComponentContext<MimicComponentType.PowerConverter>>();

const { labels, items } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PowerConverterInstance v-bind="props" />
      </NoopTooltipProvider>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
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
        v-if="source[0] === SensorComponentType.Brightloop"
        :source="source as ModuleField<SensorComponentType.Brightloop>"
        field="maxChannelTemperature"
      >
        <Partials.ListItem no-source>
          {{ items("internalTemperature") }}
          <template #value>
            <FieldRenderer.Temperature />
          </template>
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        v-if="source[0] === SensorComponentType.Ugrid"
        :source="source as ModuleField<SensorComponentType.Ugrid>"
        field="tempPowerStage"
      >
        <Partials.ListItem no-source>
          {{ items("internalTemperature") }}
          <template #value>
            <FieldRenderer.Temperature />
          </template>
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        v-if="source[0] === SensorComponentType.ShorePowerConverter"
        :source="source as ModuleField<SensorComponentType.ShorePowerConverter>"
        field="esiIgbtMaxTemperature"
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
