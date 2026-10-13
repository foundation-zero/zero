<script setup lang="ts">
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
import HeatPumpInstance from "../instances/HeatPumpInstance.vue";
import { ControlValue, ControlValueForm } from "../providers";
import * as Partials from "./partials";
import SubmitControlForm from "./partials/SubmitControlForm.vue";
const { items, labels } = useTranslations();

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
      <SensorGraph
        :device="tooltip?.technicalName ? `${tooltip.technicalName}-heat` : undefined"
        type="heat_transfers"
        field="heat"
      />
      <Partials.ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValueForm :source="controls.heatpump">
        <ControlValue
          :source="controls.heatpump"
          field="on"
        >
          <Partials.EditableListItem
            no-source
            :source="custom.controller?.controller"
          >
            {{ items("onOff") }}
          </Partials.EditableListItem>
        </ControlValue>
        <ControlValue
          :source="controls.heatpump"
          field="temperatureSetpoint"
        >
          <Partials.EditableListItem :source="parameters.temperatureSetpoint">
            {{ items("temperature") }}
          </Partials.EditableListItem>
        </ControlValue>

        <SubmitControlForm />
      </ControlValueForm>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("heatExchange") }}</TooltipListHeader>
      <Partials.ExchangeCircuit :source="sensors.heatTransfer" />
    </TooltipList>

    <TooltipList v-if="custom.controller">
      <TooltipListHeader>{{ labels("controls") }}</TooltipListHeader>
      <Partials.PIDController v-bind="custom.controller" />
    </TooltipList>
  </MimicTooltip>
</template>
