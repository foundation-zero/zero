<script setup lang="ts">
import { formatNumber } from "@/modules/common/lib/utils";
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

const formatLevel = (value: number) => formatNumber.int((value / props.maxLevel) * 100);
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
        <FieldRenderer.Percentage :format="formatLevel" />
      </span>
    </ValueListItem>
  </SensorValue>
</template>
