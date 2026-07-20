<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { RiTempColdLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { ModuleField } from "../../providers";
import SensorValue from "../../providers/SensorValue.vue";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{
  setpoint?: number;
  source: ModuleField<SensorComponentType.Temperature>;
  class?: HTMLAttributes["class"];
}>();

const { t } = useI18n();
</script>

<template>
  <SensorValue
    :source="source"
    field="temperature"
  >
    <ValueListItem :class="props.class">
      <span class="flex items-center gap-0.5">
        <slot>
          <RiTempColdLine class="text-heating-medium size-3.5" />
          {{ t("units.temperature") }}
        </slot>
      </span>
      <span class="text-foreground font-medium">
        <FieldRenderer.Temperature />
        <span v-if="setpoint != undefined">/</span>
        <FieldRenderer.Temperature
          v-if="setpoint != undefined"
          :value="setpoint"
        />
      </span>
    </ValueListItem>
  </SensorValue>
</template>
