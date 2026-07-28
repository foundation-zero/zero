<script
  setup
  lang="ts"
  generic="
    ControllerState extends ControllerStateComponentType,
    Key extends keyof ControllerStateDefinitionMap[ControllerState],
    Value extends Unstamp<ControllerStateDefinitionMap[ControllerState][Key]>
  "
>
import { unstamp } from "@/modules/common/lib/utils";
import { Unstamp } from "@/modules/common/types";
import { ControllerStateComponentType, ControllerStateDefinitionMap } from "@/modules/thrsim/types";
import { computed } from "vue";
import {
  getMimicDataProvider,
  ModuleField,
  provideFieldValue,
  provideFieldValueField,
  provideFieldValueSource,
} from ".";

const props = defineProps<{
  source: ModuleField<ControllerState>;
  field?: Key;
}>();

const { getControllerState } = getMimicDataProvider();

const controllerState = getControllerState(props.source);
const value = computed(() =>
  props.field ? (unstamp(controllerState.value?.[props.field]) as Value | undefined) : undefined,
);
provideFieldValue(value);
provideFieldValueSource(props.source);
provideFieldValueField(props.field as string | undefined);
</script>

<template>
  <slot v-bind="{ source, value, controllerState }" />
</template>
