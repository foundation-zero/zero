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
  TooltipListItemAction,
} from "../../components/tooltip-list";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { computed } from "vue";
import { MimicComponentType } from "../../types";
import { SensorGraph } from "../components/sensor-graph";
import { YardTag } from "../components/yard-tag";
import { FlowSensorInstance } from "../instances";
import { ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.FlowSensor>>();

// Only a full flow meter reports quantity and temperature; a flow-only one reports its flow.
const fullFlowSource = computed(() =>
  props.source[0] === SensorComponentType.Flow
    ? (props.source as ModuleField<SensorComponentType.Flow>)
    : undefined,
);

const { items, labels } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <FlowSensorInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <SensorGraph
        :device="tooltip?.technicalName"
        type="flows"
        field="flow"
      />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <SensorValue
        :source="source"
        field="flow"
      >
        <Partials.ListItem no-source>
          {{ items("flow") }}
        </Partials.ListItem>
      </SensorValue>
      <template v-if="fullFlowSource">
        <SensorValue
          :source="fullFlowSource"
          field="quantity"
        >
          <Partials.ListItem no-source>
            {{ items("quantity") }}
            <template #renderer>
              <FieldRenderer.QuantityLiters />
            </template>
          </Partials.ListItem>
        </SensorValue>
        <SensorValue
          :source="fullFlowSource"
          field="temperature"
        >
          <Partials.ListItem no-source>
            {{ items("temperature") }}
          </Partials.ListItem>
        </SensorValue>
      </template>
    </TooltipList>

    <TooltipList v-if="custom.controller">
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Partials.PIDController v-bind="custom.controller" />
    </TooltipList>
  </MimicTooltip>
</template>
