<script setup lang="ts" generic="Parameter extends ParametersType">
import { ParametersType } from "@/modules/thrs/types";
import { ModuleField, provideFieldValueSource } from ".";
import { createParameterFormContext, provideParameterValueForm } from "./forms.parameter";

const props = defineProps<{
  source: ModuleField<Parameter>;
}>();

provideParameterValueForm(createParameterFormContext(props.source));
provideFieldValueSource(props.source);
</script>

<template>
  <slot />
</template>
