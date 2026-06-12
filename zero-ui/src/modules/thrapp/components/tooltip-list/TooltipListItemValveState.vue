<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import { HTMLAttributes } from "vue";
import { getMimicDataProvider, ModuleField } from "../../mimics/providers/index.ts";
import { VALVE_OPEN_THRESHOLD } from "../../utils/consts.ts";
import TooltipListItemValue from "./TooltipListItemValue.vue";

const props = defineProps<{
  source: ModuleField<SensorComponentType.Valve>;
  class?: HTMLAttributes["class"];
}>();

const { getSensorValue } = getMimicDataProvider();
const valve = getSensorValue(props.source);
</script>

<template>
  <TooltipListItemValue :class="props.class">
    {{ valve?.positionRel.value! < VALVE_OPEN_THRESHOLD ? "Closed" : "Open" }}
  </TooltipListItemValue>
</template>
