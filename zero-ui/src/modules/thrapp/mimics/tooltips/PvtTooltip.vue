<script setup lang="ts">
import { usePvtMode } from "@/modules/thrapp/state";
import { RiRepeatLine } from "@remixicon/vue";
import { useRouter } from "vue-router";
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList, TooltipListHeader, TooltipListItem } from "../../components/tooltip-list";
import TooltipListItemActionButton from "../../components/tooltip-list/TooltipListItemActionButton.vue";
import { MimicComponentType } from "../../types";
import { ComponentOrientation } from "../components";
import { SensorGraph } from "../components/sensor-graph";
import { PvtInstance } from "../instances";
import { SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
import Circuit from "./partials/ExchangeCircuitPartial.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.Pvt>>();

const { labels, actions, items } = useTranslations();
const mode = usePvtMode(props.custom.group);

const { currentRoute } = useRouter();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <PvtInstance
          v-bind="props"
          :orientation="ComponentOrientation.Down"
        />
      </NoopTooltipProvider>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <SensorGraph
        :device="tooltip?.technicalName ? `${tooltip.technicalName}-heat` : undefined"
        type="heat_transfers"
        field="heat"
      />
    </TooltipList>

    <TooltipList>
      <TooltipListItem>
        &nbsp;
        <RouterLink
          v-slot="{ navigate }"
          custom
          :to="currentRoute"
        >
          <TooltipListItemActionButton @click="navigate">
            <RiRepeatLine />
            {{ actions("viewCircuitMimic") }}
          </TooltipListItemActionButton>
        </RouterLink>
      </TooltipListItem>

      <TooltipListHeader>
        {{ labels("heatExchange") }}
      </TooltipListHeader>
      <Circuit :source="sensors.heatTransfer" />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <Partials.ListItem no-source>
        {{ items("state") }}
        <template #value>
          <FieldRenderer.PvtMode :value="mode" />
        </template>
      </Partials.ListItem>
      <SensorValue
        :source="source"
        field="power"
      >
        <Partials.ListItem
          no-source
          :renderer="FieldRenderer.Power"
        >
          {{ items("electricGeneration") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
