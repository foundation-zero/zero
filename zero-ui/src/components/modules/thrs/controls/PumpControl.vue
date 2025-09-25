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
    speed: Stamped<number>;
    opTime: Stamped<number>;
    flow: Stamped<number>;
  };
  controlValues: {
    dutypoint: Stamped<number>;
    on: Stamped<boolean>;
  };
  componentName: string;
  yardTag: string;
  controlValuesQuery: string;
  module: string;
}>();
const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const { submit, isSubmitting, error, dutypoint, on } = controlValuesForm(
  props.componentName,
  "pump",
  ["dutypoint", "on"],
  props.controlValuesQuery,
  props,
  emit,
);
</script>
<template>
  <div>
    <h3>Pump Control</h3>
    <div>{{ componentName }} / {{ yardTag }}</div>
    <div>
      <label>Speed:</label>
      <NumberField
        v-model="dutypoint.value.value"
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
      <label>On:</label>
      <input
        v-model="on.value.value"
        type="checkbox"
      />
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
