<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { ModuleField, SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{
  value?: number;
  source: ModuleField<SensorComponentType.DeltaT | SensorComponentType.HeatExchanger>;
  class?: HTMLAttributes["class"];
}>();

const { t } = useI18n();
</script>

<template>
  <SensorValue
    :source="source"
    field="deltaT"
  >
    <ValueListItem :class="props.class">
      <span class="text-brand text-sm">{{ t("units.deltaT") }}</span>
      <span class="text-foreground font-medium">
        <FieldRenderer.Temperature :value="value" />
      </span>
    </ValueListItem>
  </SensorValue>
</template>
