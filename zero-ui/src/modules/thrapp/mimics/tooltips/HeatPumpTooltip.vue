<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import HeatPumpInstance from "../instances/HeatPumpInstance.vue";
import { ControlValue, ControlValueForm, SensorValue } from "../providers";
import * as Partials from "./partials";
import SubmitControlForm from "./partials/SubmitControlForm.vue";
const { items, labels, sources } = useTranslations();

const props = defineProps<TooltipComponentContext<MimicComponentType.HeatPump>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <HeatPumpInstance
          v-bind="props"
          force-height
        />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <Partials.ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValueForm :source="controls.heatpump">
        <ControlValue
          :source="controls.heatpump"
          field="on"
        >
          <Partials.EditableListItem>
            {{ items("onOff") }}
            <template #sourceName>
              {{ sources("this") }}
            </template>
          </Partials.EditableListItem>
        </ControlValue>
        <ControlValue
          :source="controls.heatpump"
          field="temperatureSetpoint"
        >
          <Partials.EditableListItem>
            {{ items("temperature") }}
            <template #sourceName>
              {{ sources("this") }}
            </template>
          </Partials.EditableListItem>
        </ControlValue>

        <SubmitControlForm />
      </ControlValueForm>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="heat"
      >
        <Partials.ListItem>
          {{ items("heatExchange") }}
          <template #sourceName>
            {{ sources("calculated") }}
          </template>
        </Partials.ListItem>
      </SensorValue>
      <Partials.Circuit
        :delta-t="source"
        :incoming="sensors.incoming"
        :outgoing="sensors.outgoing"
      />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("controls") }}</TooltipListHeader>
      <Partials.PIDController
        :type="SensorComponentType.Flow"
        :controller="controllerState.controller"
        :setpoint="parameters.flow"
        :measurement="sensors.measurement"
      />
    </TooltipList>
  </MimicTooltip>
</template>
