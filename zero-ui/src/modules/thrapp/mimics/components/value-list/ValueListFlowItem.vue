<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { RiDropLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { ModuleField } from "../../providers";
import SensorValue from "../../providers/SensorValue.vue";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{
  source: ModuleField<SensorComponentType.Flow | SensorComponentType.CalculatedFlow>;
  class?: HTMLAttributes["class"];
}>();

const { t } = useI18n();
</script>

<template>
  <SensorValue
    :source="source"
    field="flow"
  >
    <ValueListItem :class="props.class">
      <span class="flex items-center gap-0.5">
        <RiDropLine class="text-brand size-3.5" />
        {{ t("units.flow") }}
      </span>
      <span class="text-foreground font-medium">
        <FieldRenderer.FlowRate />
      </span>
    </ValueListItem>
  </SensorValue>
</template>
