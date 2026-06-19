<script setup lang="ts">
import { TooltipList } from "../../components/tooltip-list/index.ts";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { ManualValveType } from "../components/manual-valve/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import ManualValveInstance from "../instances/ManualValveInstance.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.ManualValve>>();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <ManualValveInstance
        v-bind="props"
        :type="ManualValveType.Switch"
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
    </TooltipList>
  </MimicTooltip>
</template>
