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
  TooltipListItemAction,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import { FieldEditor } from "../editors";
import PumpInstance from "../instances/PumpInstance.vue";
import { ControlValue, ControlValueForm, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import ComponentInfo from "./partials/ComponentInfo.vue";
import FlowController from "./partials/FlowController.vue";
import ManualControl from "./partials/ManualControl.vue";
import SubmitControlForm from "./partials/SubmitControlForm.vue";
import TemperatureController from "./partials/TemperatureController.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.Pump>>();

const { labels, actions, items, sources } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PumpInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValueForm :source="controls.pump">
        <ControlValue
          :source="controls.pump"
          field="dutypoint"
        >
          <TooltipListItem>
            <TooltipListItemTitle>
              {{ items("relativeDutyPoint") }}
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
          :source="controls.pump"
          field="on"
        >
          <TooltipListItem>
            <TooltipListItemTitle>
              {{ items("onOff") }}
              <FieldRenderer.Source>
                {{ sources("this") }}
              </FieldRenderer.Source>
            </TooltipListItemTitle>
            <FieldEditor.Auto>
              <TooltipListItemValue>
                <FieldRenderer.OnOff />
              </TooltipListItemValue>
            </FieldEditor.Auto>
          </TooltipListItem>
        </ControlValue>
        <SubmitControlForm />
      </ControlValueForm>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="sensors.pressure"
        field="pressure"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("pressure") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Pressure />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="flow"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("flow") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.FlowRate />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("energyConsumption") }}
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.Energy :value="600" />
        </TooltipListItemValue>
      </TooltipListItem>
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("powerInput") }}
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.Power :value="200" />
        </TooltipListItemValue>
      </TooltipListItem>
      <SensorValue
        :source="source"
        field="speed"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("speed") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Frequency />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <SensorValue
        :source="source"
        field="opTime"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("operationTime") }}
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.TimeRemaining />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("totalRunningHours") }}
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.TimeRemaining :value="25 * 60 + 31" />
        </TooltipListItemValue>
      </TooltipListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ actions("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <FlowController
        :controller="controllerState.flowController"
        :measurement="sensors.flowMeasurement"
        :setpoint="parameters.flow"
      >
        {{ sources("pumpFlowController") }}
      </FlowController>
      <TemperatureController
        :controller="controllerState.temperatureController"
        :measurement="sensors.temperatureMeasurement"
        :setpoint="parameters.temperature"
      >
        {{ sources("pumpTemperatureController") }}
      </TemperatureController>
    </TooltipList>
  </MimicTooltip>
</template>
