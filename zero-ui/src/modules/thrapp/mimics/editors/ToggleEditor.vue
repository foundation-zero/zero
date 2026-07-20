<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { cn } from "@/modules/common/lib/utils.ts";
import { ParametersType } from "@/modules/thrs/types/index.ts";
import { computed, toRef } from "vue";
import { injectValueForm } from "../providers/forms.ts";
import { getFieldValue, injectFieldValueSource } from "../providers/index.ts";
import EditableField from "./EditableField.vue";
import { FieldEditorProps } from "./index.ts";

const props = defineProps<FieldEditorProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));
const form = injectValueForm();
const source = injectFieldValueSource();

const enabled = computed({
  get() {
    if (source?.[0] === ParametersType.Disabled) {
      return !value.value;
    } else {
      return value.value;
    }
  },
  set(enabled: boolean) {
    if (source?.[0] === ParametersType.Disabled) {
      value.value = !enabled;
    } else {
      value.value = enabled;
    }
  },
});
</script>

<template>
  <span :class="cn('flex items-center gap-2', props.class)">
    <EditableField>
      <slot />
      <template #editor>
        <slot />
        <Switch
          v-model="enabled"
          :autofocus="form?.hasFocus"
          :disabled="form?.isPending.value || !form?.isEditable.value"
        />
      </template>
    </EditableField>
  </span>
</template>
