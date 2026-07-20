<script setup lang="ts">
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import NumberFieldPrefix from "@/components/ui/number-field/NumberFieldPrefix.vue";
import { cn } from "@/modules/common/lib/utils.ts";
import { injectValueForm } from "../providers/forms.ts";
import EditableField from "./EditableField.vue";
import { FieldEditor, injectMultiLineEditor, NumberEditorProps } from "./index.ts";

const props = withDefaults(defineProps<NumberEditorProps>(), {});

const modelValue = defineModel<number | undefined>("modelValue", {
  required: true,
});

const isMultiLineEditor = injectMultiLineEditor();
const form = injectValueForm();
</script>

<template>
  <EditableField>
    <slot />
    <template #editor>
      <NumberField
        v-model="modelValue"
        :class="cn({ 'w-full': isMultiLineEditor, 'w-30': !isMultiLineEditor }, props.class)"
        :readonly="form?.isPending.value"
        :disabled="!form?.isEditable.value"
        v-bind="props"
      >
        <NumberFieldContent>
          <NumberFieldDecrement class="text-brand" />
          <NumberFieldInput
            :autofocus="form?.hasFocus"
            class="bg-muted h-9 rounded-xs"
          />
          <NumberFieldIncrement class="text-brand" />
          <NumberFieldPrefix v-if="form?.isPending.value">
            <FieldEditor.PendingIndicator />
          </NumberFieldPrefix>
        </NumberFieldContent>
      </NumberField>
    </template>
  </EditableField>
</template>
