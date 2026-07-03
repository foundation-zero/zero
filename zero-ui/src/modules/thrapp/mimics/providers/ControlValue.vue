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
import { ModuleField, provideFieldValueSource } from ".";
import { provideControlValue } from "./forms";

const props = defineProps<{
  source: ModuleField<Control>;
  field?: Key;
}>();

const value = provideControlValue<Control, Key>(props.source, props.field);
provideFieldValueSource(props.source);
</script>

<template>
  <slot v-bind="{ source, value: value as Value }" />
</template>
