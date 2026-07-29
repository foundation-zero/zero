<script
  setup
  lang="ts"
  generic="
    Sensor extends SensorComponentType,
    Key extends keyof SensorDefinitionMap[Sensor],
    Value extends Unstamp<SensorDefinitionMap[Sensor][Key]>
  "
>
import { unstamp } from "@/modules/common/lib/utils";
import { Unstamp } from "@/modules/common/types";
import { SensorComponentType, SensorDefinitionMap } from "@/modules/thrsim/types";
import { computed } from "vue";
import {
  DEFAULT_SENSOR_FIELD_VALUE_FIELD,
  getMimicDataProvider,
  ModuleField,
  provideFieldValue,
  provideFieldValueField,
  provideFieldValueSource,
} from ".";

const props = defineProps<{
  source: ModuleField<Sensor>;
  field?: Key;
}>();

const { getSensorValue } = getMimicDataProvider();

const field = props.field ?? DEFAULT_SENSOR_FIELD_VALUE_FIELD[props.source[0]];
const sensor = getSensorValue(props.source);
const value = computed(() =>
  field ? (unstamp(sensor.value?.[field as Key]) as Value | undefined) : undefined,
);
provideFieldValue(value);
provideFieldValueSource(props.source);
provideFieldValueField(field as string | undefined);
</script>

<template>
  <slot v-bind="{ value, source, sensor }" />
</template>
