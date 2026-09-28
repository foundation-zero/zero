<script setup lang="ts">
import { ratioToPercentage } from "@/modules/common/lib/numbers";
import { SensorComponentType } from "@/modules/thrsim/types/index.ts";
import { RiWaterPercentLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { ModuleField, SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{
  maxLevel: number;
  source: ModuleField<SensorComponentType.Level>;
  class?: HTMLAttributes["class"];
}>();

const { t } = useI18n();

const transform = (value: number) => ratioToPercentage(value / props.maxLevel);
</script>

<template>
  <SensorValue
    :source="source"
    field="level"
  >
    <ValueListItem :class="props.class">
      <span class="flex items-center gap-0.5">
        <RiWaterPercentLine class="text-brand size-3.5" />
        {{ t("units.level") }}
      </span>
      <span class="text-foreground font-medium">
        <FieldRenderer.Percentage :transform="transform" />
      </span>
    </ValueListItem>
  </SensorValue>
</template>
