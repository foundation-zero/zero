<script setup lang="ts">
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import EditableField from "./EditableField.vue";
import { NumberEditorProps } from "./index.ts";

const props = withDefaults(defineProps<NumberEditorProps>(), {});

const modelValue = defineModel<number | undefined>("modelValue", {
  required: true,
});
</script>

<template>
  <EditableField>
    <slot />
    <template #editor>
      <NumberField
        v-model="modelValue"
        class="w-30"
        v-bind="props"
      >
        <NumberFieldContent>
          <NumberFieldDecrement class="text-brand" />
          <NumberFieldInput class="bg-muted h-9 rounded-xs" />
          <NumberFieldIncrement class="text-brand" />
        </NumberFieldContent>
      </NumberField>
    </template>
  </EditableField>
</template>
