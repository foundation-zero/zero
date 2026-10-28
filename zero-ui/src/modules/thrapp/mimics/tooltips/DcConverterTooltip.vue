<script setup lang="ts">
import { ControllerStateComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
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
import { DcConverterInstance } from "../instances";
import { getField, getMimicDataProvider, ModuleField, SensorValue } from "../providers";
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
      <SensorValue
        :source="source"
        field="totalPower"
      >
        <Partials.ListItem no-source>
          {{ items("power") }}
          <template #value>
            <FieldRenderer.Power />
          </template>
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        v-if="source[0] === SensorComponentType.UgridGroup"
        :source="source as ModuleField<SensorComponentType.UgridGroup>"
        field="maxTempPowerStage"
      >
        <Partials.ListItem no-source>
          {{ items("internalTemperature") }}
          <template #value>
            <FieldRenderer.Temperature />
          </template>
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        v-if="source[0] === SensorComponentType.BrightloopGroup"
        :source="source as ModuleField<SensorComponentType.BrightloopGroup>"
        field="maxChannelTemperature"
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
