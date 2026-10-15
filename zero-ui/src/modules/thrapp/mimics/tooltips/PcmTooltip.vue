<script setup lang="ts">
import { ControllerStateComponentType } from "@/modules/thrsim/types";
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { SensorGraph } from "../components/sensor-graph";
import { YardTag } from "../components/yard-tag";
import { PcmInstance } from "../instances";
import { ControllerStateValue, getField } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
const { items, labels } = useTranslations();

const props = defineProps<TooltipComponentContext<MimicComponentType.Pcm>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PcmInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <SensorGraph
        :device="tooltip?.technicalName ? `${tooltip.technicalName}-heat` : undefined"
        type="heat_transfers"
        field="heat"
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
          <ControllerStateValue
            :source="controllerState.chargeController"
            field="chargingState"
          >
            <FieldRenderer.ChargingMode />
          </ControllerStateValue>
        </template>
      </Partials.ListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <Partials.ExchangeCircuit :source="sensors.heatTransfer" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <Partials.ListItem no-source>
        {{ items("charged") }}
        <template #value>
          <ControllerStateValue
            :source="controllerState.chargeController"
            field="chargeStatus"
          >
            <FieldRenderer.ChargeState />
          </ControllerStateValue>
        </template>
      </Partials.ListItem>
      <Partials.ListItem no-source>
        {{ items("estBatteryLoad") }}
        <template #renderer>
          <ControllerStateValue
            :source="controllerState.chargeController"
            field="energy"
          >
            <FieldRenderer.Auto />
          </ControllerStateValue>
          <ControllerStateValue
            :source="controllerState.chargeController"
            field="charge"
          >
            <FieldRenderer.Percentage />
          </ControllerStateValue>
        </template>
      </Partials.ListItem>
    </TooltipList>
  </MimicTooltip>
</template>
