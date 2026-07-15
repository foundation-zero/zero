<script
  setup
  lang="ts"
  generic="
    Control extends ControlComponentType,
    Key extends keyof ControlDefinitionMap[Control],
    Value extends Unstamp<ControlDefinitionMap[Control][Key]>
  "
>
import { Unstamp } from "@/modules/common/types";
import { ControlComponentType, ControlDefinitionMap } from "@/modules/thrs/types";
import {
  DEFAULT_CONTROL_FIELD_VALUE_FIELD,
  ModuleField,
  provideFieldValueField,
  provideFieldValueSource,
} from ".";
import { provideControlValue } from "./forms.control";

const props = defineProps<{
  source: ModuleField<Control>;
  field?: Key;
}>();

const value = provideControlValue<Control, Key>(props.source, props.field);
const field = props.field ?? DEFAULT_CONTROL_FIELD_VALUE_FIELD[props.source[0]];
provideFieldValueSource(props.source);
provideFieldValueField(field as string | undefined);
</script>

<template>
  <slot v-bind="{ source, value: value as Value }" />
</template>
