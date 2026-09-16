<script setup lang="ts">
import { RiRepeatLine } from "@remixicon/vue";
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemTitle,
} from "../../components/tooltip-list";
import TooltipListItemActionButton from "../../components/tooltip-list/TooltipListItemActionButton.vue";
import { MimicComponentType } from "../../types";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from "../components/mode-badge";
import { YardTag } from "../components/yard-tag";
import ConnectingCircuit from "../instances/components/ConnectingCircuit.vue";
import { SensorValue } from "../providers";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.ConnectingCircuit>>();

const { items, labels, actions } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <ConnectingCircuit
        class="w-49"
        v-bind="props"
      />

      <YardTag class="text-sm">{{
        custom.consumingCircuit ? labels("connectingCircuit") : labels("consumingCircuit")
      }}</YardTag>
    </div>

    <TooltipList
      v-if="tooltip?.componentType || tooltip?.mqttTopic || tooltip?.technicalName"
      class="border-b-0"
    >
      <Partials.ComponentInfo :tooltip="tooltip" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader v-if="custom.consumingCircuit">
        &nbsp;
        <TooltipListItemActionButton>
          <RiRepeatLine />
          {{ actions("viewCircuitMimic") }}
        </TooltipListItemActionButton>
      </TooltipListHeader>

      <TooltipListHeader>
        {{ tooltip?.title }}
      </TooltipListHeader>
      <Partials.ListItem v-if="!custom.consumingCircuit">
        {{ items("mode") }}
        <template #value>
          <ModeBadge
            :mode="ModeBadgeMode.Using"
            :label="labels('consuming')"
            :size="ModeBadgeSize.Circuit"
          />
        </template>
      </Partials.ListItem>

      <TooltipListItem>
        <TooltipListItemTitle>{{ items("temperature") }}</TooltipListItemTitle>
      </TooltipListItem>
      <SensorValue
        :source="sensors.tIn"
        field="temperature"
      >
        <Partials.ListItem size="sm">
          {{ items("incomingTemperature") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.tOut"
        field="temperature"
      >
        <Partials.ListItem size="sm">
          {{ items("outgoingTemperature") }}
        </Partials.ListItem>
      </SensorValue>
      <TooltipListItem>
        <TooltipListItemTitle>{{ items("flow") }}</TooltipListItemTitle>
      </TooltipListItem>
      <SensorValue
        :source="sensors.flowIn"
        field="flow"
      >
        <Partials.ListItem size="sm">
          {{ items("incomingFlow") }}
        </Partials.ListItem>
      </SensorValue>
      <SensorValue
        :source="sensors.flowOut"
        field="flow"
      >
        <Partials.ListItem size="sm">
          {{ items("outgoingFlow") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
