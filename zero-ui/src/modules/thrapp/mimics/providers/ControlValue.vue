<script
  setup
  lang="ts"
  generic="
    Control extends ControlComponentType,
    Key extends keyof ControlDefinitionMap[Control],
    Value extends Unstamp<ControlDefinitionMap[Control][Key]>
  "
>
import { unstamp } from "@/modules/common/lib/utils";
import { Unstamp } from "@/modules/common/types";
import { ControlComponentType, ControlDefinitionMap } from "@/modules/thrs/types";
import { computed } from "vue";
import { getMimicDataProvider, ModuleField, provideFieldValue, provideFieldValueSource } from ".";

const props = defineProps<{
  source: ModuleField<Control>;
  field?: Key;
}>();

const { getControlValue } = getMimicDataProvider();

const control = getControlValue(props.source);
const value = computed(() =>
  props.field ? (unstamp(control.value?.[props.field]) as Value | undefined) : undefined,
);
provideFieldValue(value);
provideFieldValueSource(props.source);
</script>

<template>
  <slot v-bind="{ source, value, control }" />
</template>
