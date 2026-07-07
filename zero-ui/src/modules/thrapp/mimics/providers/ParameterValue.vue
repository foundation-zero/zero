<script
  setup
  lang="ts"
  generic="
    Parameter extends ParametersType,
    Value extends Unstamp<ParameterDefinitionMap[Parameter]>
  "
>
import { Unstamp } from "@/modules/common/types";
import { ParameterDefinitionMap, ParametersType } from "@/modules/thrs/types";
import { getMimicDataProvider, ModuleField, provideFieldValue, provideFieldValueSource } from ".";

const props = defineProps<{
  source: ModuleField<Parameter>;
}>();

const { getParameter: getParameterValue } = getMimicDataProvider();

const parameter = getParameterValue(props.source);

provideFieldValue(parameter);
provideFieldValueSource(props.source);
</script>

<template>
  <slot v-bind="{ value: parameter as Value, parameter, source }" />
</template>
