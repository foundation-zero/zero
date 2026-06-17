<script setup lang="ts">
import { TooltipList } from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import LoopCircuitInstance from "../instances/LoopCircuitInstance.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.ExchangeCircuit>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <LoopCircuitInstance
        v-bind="props"
        force-height
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>
  </MimicTooltip>
</template>
