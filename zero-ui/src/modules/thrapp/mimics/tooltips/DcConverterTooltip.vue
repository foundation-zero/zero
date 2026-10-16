<script setup lang="ts">
import { ControllerStateComponentType } from "@/modules/thrsim/types";
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { useDcMode } from "../../state";
import { MimicComponentType } from "../../types";
import { DcMode } from "../components/dc-converter";
import { SensorGraph } from "../components/sensor-graph";
import { YardTag } from "../components/yard-tag";
import { DcConverterInstance } from "../instances";
import { getField, getMimicDataProvider, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
const { items, labels } = useTranslations();

const props = defineProps<TooltipComponentContext<MimicComponentType.DcConverter>>();

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();

const modeKey = useDcMode(props.custom.group);
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <DcConverterInstance
          v-bind="props"
          force-height
        />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <SensorGraph
        :device="tooltip?.technicalName ? `${tooltip.technicalName}-heat` : undefined"
        type="heat_transfers"
        :field="['heat', 'flow', 'delta_t']"
      />
      <Partials.ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <Partials.ListItem>
        {{ items("state") }}
        <template #source>
          <FieldRenderer.Source
            :source="getField(ControllerStateComponentType.PIDController, 'dhw', 'placeholder')"
          />
        </template>
        <template #value>
          <DcMode
            :mode="modeKey"
            :state="state"
          />
        </template>
      </Partials.ListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <Partials.ExchangeCircuit :source="sensors.heatTransfer" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue :source="sensors.power">
        <Partials.ListItem no-source>
          {{ items("power") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue :source="sensors.temperature">
        <Partials.ListItem no-source>
          {{ items("internalTemperature") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
