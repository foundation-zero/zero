<script setup lang="ts">
import { usePvtMode } from "@/modules/thrapp/state";
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
import { MimicComponentType } from "../../types";
import { ComponentOrientation } from "../components";
import { PvtInstance } from "../instances";
import { FieldRenderer } from "../renderers";
import * as Partials from "./partials";
import Circuit from "./partials/Circuit.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.Pvt>>();

const { labels, actions, items } = useTranslations();
const mode = usePvtMode(props.custom.group);
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
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("mode") }}
        <TooltipListItemAction>{{ actions("viewCircuitMimic") }}</TooltipListItemAction>
      </TooltipListHeader>
      <Partials.ListItem no-source>
        {{ items("pvt") }}
        <template #value>
          <FieldRenderer.PvtMode :value="mode" />
        </template>
      </Partials.ListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("thisCircuit") }}
      </TooltipListHeader>
      <Circuit
        :incoming="sensors.incoming"
        :outgoing="sensors.outgoing"
        :delta-t="source"
        :flow="sensors.flow"
      />
    </TooltipList>
  </MimicTooltip>
</template>
