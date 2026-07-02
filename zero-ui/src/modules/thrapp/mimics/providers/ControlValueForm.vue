<script setup lang="ts" generic="Control extends ControlComponentType">
import { ControlComponentType } from "@/modules/thrs/types";
import { ModuleField } from ".";
import { createFormContext, provideControlValueForm } from "./forms";

const props = defineProps<{
  source: ModuleField<Control>;
}>();

provideControlValueForm(createFormContext(props.source));
</script>

<template>
  <slot />
</template>
