<script setup lang="ts">
import { RiFireLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

import { SensorComponentType } from "@/modules/thrsim/types/index.ts";
import { ModuleField } from "../../providers";
import SensorValue from "../../providers/SensorValue.vue";

const props = defineProps<{
  value?: number;
  source: ModuleField<SensorComponentType.HeatExchanger>;
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <SensorValue
    :source="source"
    field="heat"
  >
    <ValueListItem :class="props.class">
      <span class="flex items-center gap-0.5">
        <RiFireLine class="text-heating-medium size-3.5" />
      </span>
      <span class="text-foreground font-medium">
        <FieldRenderer.Heat :value="value" />
      </span>
    </ValueListItem>
  </SensorValue>
</template>
