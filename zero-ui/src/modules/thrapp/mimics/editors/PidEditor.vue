<script setup lang="ts">
import type { TupleIndices } from "@/modules/common/types";
import { PID } from "@/modules/thrsim/types";
import { computed } from "vue";
import { FieldEditor, NumberEditorProps } from ".";
import { getFieldValue } from "../providers";

const props = withDefaults(defineProps<NumberEditorProps<PID> & { part: TupleIndices<PID> }>(), {});
const tuning = getFieldValue<PID>();
const value = computed({
  get() {
    return tuning.value?.[props.part];
  },
  set(newValue: number) {
    if (!tuning.value) return;

    tuning.value[props.part] = newValue;
    tuning.value = [...tuning.value];
  },
});
</script>

<template>
  <FieldEditor.Number
    v-model="value"
    :format-options="formatOptions"
    :min="-100"
    :max="100"
    :step="0.001"
    :class="props.class"
  >
    <slot />
  </FieldEditor.Number>
</template>
