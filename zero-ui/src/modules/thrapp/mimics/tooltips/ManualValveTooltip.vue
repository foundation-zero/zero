<script setup lang="ts">
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import { TooltipList } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { ManualValveType } from "../components/manual-valve";
import { YardTag } from "../components/yard-tag";
import ManualValveInstance from "../instances/ManualValveInstance.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.ManualValve>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <ManualValveInstance
          v-bind="props"
          :type="ManualValveType.Switch"
        />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>
  </MimicTooltip>
</template>
