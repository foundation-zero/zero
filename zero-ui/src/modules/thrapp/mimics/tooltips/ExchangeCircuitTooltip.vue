<script setup lang="ts">
import { RiRepeatLine } from "@remixicon/vue";
import { useRouter } from "vue-router";
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import { TooltipList, TooltipListHeader, TooltipListItem } from "../../components/tooltip-list";
import TooltipListItemActionButton from "../../components/tooltip-list/TooltipListItemActionButton.vue";
import { MimicComponentType } from "../../types";
import { ModeBadges, ModeBadgeSize } from "../components/mode-badge";
import { SensorGraph } from "../components/sensor-graph";
import { YardTag } from "../components/yard-tag";
import ExchangeCircuit from "../instances/content/ExchangeCircuitContent.vue";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.ExchangeCircuit>>();
const { currentRoute } = useRouter();
const { labels, actions } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <ExchangeCircuit
        class="w-49"
        v-bind="props"
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <SensorGraph
      :device="tooltip?.technicalName"
      type="heat_transfers"
      field="heat"
    />

    <TooltipList>
      <TooltipListItem v-if="custom.modeModule">
        &nbsp;
        <RouterLink :to="{ name: currentRoute.name, params: { module: custom.modeModule } }">
          <TooltipListItemActionButton>
            <RiRepeatLine />
            {{ actions("viewCircuitMimic") }}
          </TooltipListItemActionButton>
        </RouterLink>
      </TooltipListItem>
      <TooltipListHeader>
        {{ custom.circuitName }}
      </TooltipListHeader>

      <Partials.ListItem v-if="custom.modeModule">
        {{ labels("mode") }}
        <template #value>
          <ModeBadges
            :module="custom.modeModule"
            :size="ModeBadgeSize.Circuit"
          />
        </template>
      </Partials.ListItem>
      <Partials.ExchangeCircuit :source="source" />
    </TooltipList>
  </MimicTooltip>
</template>
