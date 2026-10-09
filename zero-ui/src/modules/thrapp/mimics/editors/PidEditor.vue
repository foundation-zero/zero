<script setup lang="ts">
import type { TupleIndices } from "@/modules/common/types";
import { PID } from "@/modules/thrsim/types";
import { computed } from "vue";
import { FieldEditor, NumberEditorProps } from ".";
import { getFieldValue } from "../providers";

const props = withDefaults(defineProps<NumberEditorProps<PID> & { part: TupleIndices<PID> }>(), {
  formatOptions: () => ({ maximumFractionDigits: 5 }),
});
const tuning = getFieldValue<PID>();
const value = computed({
  get() {
    return tuning.value?.[props.part];
  },
  set(newValue: number) {
    if (!tuning.value) return;

    const updatedTuning: PID = [...tuning.value];
    updatedTuning[props.part] = newValue;
    tuning.value = updatedTuning;
  },
});
</script>

<template>
  <FieldEditor.Number
    v-model="value"
    :format-options="formatOptions"
    :min="-100"
    :max="100"
    :step="0.00001"
    :class="props.class"
  >
    <slot />
  </FieldEditor.Number>
</template>
