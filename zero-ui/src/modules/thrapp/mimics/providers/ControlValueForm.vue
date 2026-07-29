<script
  setup
  lang="ts"
  generic="Control extends ControlComponentType, Key extends keyof ControlDefinitionMap[Control]"
>
import { ControlComponentType, ControlDefinitionMap } from "@/modules/thrsim/types";
import { DEFAULT_CONTROL_FIELD_VALUE_FIELD, ModuleField } from ".";
import { createFormContext, provideControlValue, provideControlValueForm } from "./forms.control";

const props = defineProps<{
  source: ModuleField<Control>;
  field?: Key;
}>();

const form = createFormContext(props.source);
const field = props.field ?? DEFAULT_CONTROL_FIELD_VALUE_FIELD[props.source[0]];
provideControlValueForm(form);
provideControlValue<Control>(props.source, field, form);
</script>

<template>
  <slot />
</template>
