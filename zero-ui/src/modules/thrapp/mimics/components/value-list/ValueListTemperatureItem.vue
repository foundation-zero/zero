<script
  setup
  lang="ts"
  generic="
    Type extends
      | SensorComponentType.Temperature
      | SensorComponentType.CalculatedTemperature
      | SensorComponentType.HeatTransferDevice
  "
>
import { SensorComponentType, SensorDefinitionMap } from "@/modules/thrsim/types/index.ts";
import { RiTempColdLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { ModuleField } from "../../providers";
import SensorValue from "../../providers/SensorValue.vue";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

const props = withDefaults(
  defineProps<{
    setpoint?: number;
    source: ModuleField<Type>;
    class?: HTMLAttributes["class"];
    field?: keyof SensorDefinitionMap[Type];
    temperatureLabel?: string;
  }>(),
  { field: "temperature" as unknown as undefined },
);

const { t } = useI18n();
</script>

<template>
  <SensorValue
    :source="source"
    :field="field"
  >
    <ValueListItem :class="props.class">
      <span class="flex items-center gap-0.5">
        <slot>
          <span v-if="temperatureLabel">
            {{ t("units.temp") }}<small>{{ t(`temperatureLabels.${temperatureLabel}`) }}</small>
          </span>
          <template v-else>
            <RiTempColdLine class="text-heating-medium size-3.5" />
            {{ t("units.temperature") }}
          </template>
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
