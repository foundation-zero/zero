<script setup lang="ts">
import { HTMLAttributes } from "vue";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

import { SensorComponentType } from "@/modules/thrsim/types/index.ts";
import { RiFlashlightLine } from "@remixicon/vue";
import { ModuleField } from "../../providers";
import SensorValue from "../../providers/SensorValue.vue";
const props = defineProps<{
  value?: number;
  source: ModuleField<SensorComponentType.Pvt | SensorComponentType.Thruster>;
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <SensorValue :source="source">
    <ValueListItem :class="props.class">
      <span class="flex items-center gap-0.5">
        <RiFlashlightLine class="text-constructive size-3.5" />
      </span>
      <span class="text-foreground font-medium">
        <FieldRenderer.Power />
      </span>
    </ValueListItem>
  </SensorValue>
</template>
