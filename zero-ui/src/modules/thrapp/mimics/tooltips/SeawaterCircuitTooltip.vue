<script setup lang="ts">
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import { TooltipList, TooltipListHeader } from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag";
import SeawaterCircuitContent from "../instances/content/SeawaterCircuitContent.vue";
import { SensorValue } from "../providers";
import * as Partials from "./partials";
const props = defineProps<TooltipComponentContext<MimicComponentType.SeawaterCircuit>>();

const { items } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <SeawaterCircuitContent
        v-bind="props"
        class="w-49"
      />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList>
      <TooltipListHeader>
        {{ custom.circuitName }}
      </TooltipListHeader>
      <SensorValue
        :source="source"
        field="temperature"
      >
        <Partials.ListItem>
          {{ items("temperature") }}
        </Partials.ListItem>
      </SensorValue>
    </TooltipList>
  </MimicTooltip>
</template>
