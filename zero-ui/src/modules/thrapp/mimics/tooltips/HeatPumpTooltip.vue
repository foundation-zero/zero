<script setup lang="ts">
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import { FieldEditor } from "../editors";
import HeatPumpInstance from "../instances/HeatPumpInstance.vue";
import { ControlValue, ControlValueForm, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";
import ManualControl from "./partials/ManualControl.vue";
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
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValueForm :source="controls.heatpump">
        <ControlValue
          :source="controls.heatpump"
          field="on"
        >
          <TooltipListItem>
            <TooltipListItemTitle>
              {{ items("onOff") }}
              <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
            </TooltipListItemTitle>

            <FieldEditor.Auto>
              <TooltipListItemValue>
                <FieldRenderer.Auto />
              </TooltipListItemValue>
            </FieldEditor.Auto>
          </TooltipListItem>
        </ControlValue>
        <ControlValue
          :source="controls.heatpump"
          field="temperatureSetpoint"
        >
          <TooltipListItem>
            <TooltipListItemTitle>
              {{ items("temperature") }}
              <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
            </TooltipListItemTitle>
            <FieldEditor.Auto>
              <TooltipListItemValue>
                <FieldRenderer.Auto />
              </TooltipListItemValue>
            </FieldEditor.Auto>
          </TooltipListItem>
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
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("heatExchange") }}
            <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Auto />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="deltaT"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("deltaTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Auto />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.incoming"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("incomingTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Auto />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.outgoing"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("outgoingTemperature") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Auto />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("controls") }}</TooltipListHeader>
      <FlowController
        :controller="controllerState.controller"
        :setpoint="parameters.flow"
        :measurement="sensors.measurement"
      />
    </TooltipList>
  </MimicTooltip>
</template>
