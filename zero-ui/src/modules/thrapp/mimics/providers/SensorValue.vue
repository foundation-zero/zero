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
import { SensorComponentType, SensorDefinitionMap } from "@/modules/thrs/types";
import { computed } from "vue";
import { getMimicDataProvider, ModuleField, provideFieldValue, provideFieldValueSource } from ".";

const props = defineProps<{
  source: ModuleField<Sensor>;
  field?: Key;
}>();

const { getSensorValue } = getMimicDataProvider();

const sensor = getSensorValue(props.source);
const value = computed(() =>
  props.field ? (unstamp(sensor.value?.[props.field]) as Value | undefined) : undefined,
);
provideFieldValue(value);
provideFieldValueSource(props.source);
</script>

<template>
  <slot v-bind="{ value, source, sensor }" />
</template>
