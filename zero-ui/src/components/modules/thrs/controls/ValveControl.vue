<script setup lang="ts">
import { type Stamped } from "@/@types/thrs";
import { Button } from "@/components/ui/shadcn/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/shadcn/number-field";
import { controlValuesForm } from "@/stores/thrs";

const props = defineProps<{
  sensorValues: {
    position_rel: Stamped<number>;
  };
  controlValues: {
    setpoint: Stamped<number>;
  };
  controlValuesQuery: string;
  componentName: string;
  yardTag: string;
  valveType: string;
  module: string;
}>();
const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const { submit, isSubmitting, error, setpoint } = controlValuesForm(
  props.componentName,
  "valve",
  ["setpoint"],
  props.controlValuesQuery,
  props,
  emit,
);
</script>
<template>
  <div>
    <h3>Valve Control</h3>
    <div>{{ componentName }} / {{ yardTag }} / {{ valveType }}</div>
    <div>
      <label>Setpoint:</label>
      <NumberField
        v-model="setpoint.value.value"
        :step="0.1"
        :min="0"
        :max="1"
      >
        <NumberFieldContent>
          <NumberFieldDecrement />
          <NumberFieldInput />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>
    </div>
    <div>
      <Button
        :disabled="isSubmitting"
        @click="submit"
      >
        {{ isSubmitting ? "Submitting..." : "Submit" }}
      </Button>
      <div
        v-if="error"
        class="text-red-500"
      >
        {{ error }}
      </div>
    </div>
  </div>
</template>
