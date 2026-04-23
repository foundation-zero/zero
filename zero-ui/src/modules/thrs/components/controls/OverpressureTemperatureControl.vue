<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import { ThrsSimulationType } from "@/modules/thrs/lib/consts";
import { controlValuesForm, MutationType } from "@/modules/thrs/stores/thrs";
import { OverpressureTemperatureSimulation } from "@/modules/thrs/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { RiLoader2Line, RiSendPlaneLine } from "@remixicon/vue";
import { toRef } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  values: OverpressureTemperatureSimulation;
  componentName: string;
  query: string;
  simulation: ThrsSimulationType;
}>();

const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const values = toRef(props, "values");

const { submit, isSubmitting, error, overpressure, temperature } = controlValuesForm(
  props.simulation,
  MutationType.Simulation,
  "OverpressureTemperatureBoundaryInputType!",
  props.componentName,
  values,
  ["temperature", "overpressure"],
  props.query,
  emit,
);
</script>

<template>
  <div class="bg-background flex flex-col rounded-md border p-4 shadow-md">
    <h3 class="overflow-hidden font-semibold text-ellipsis whitespace-nowrap capitalize">
      {{ toUpperCamelCase(componentName) }}
    </h3>

    <div class="mt-6 grid grid-cols-2 gap-x-2">
      <div class="grid gap-1.5">
        <header class="text-2xs tracking-wide uppercase">
          {{ t("components.inputs.temperature.label") }}
        </header>
        <NumberField
          v-model="temperature.value.value"
          class="grow"
          :step="1"
          :min="0"
          :max="100"
        >
          <NumberFieldContent>
            <NumberFieldDecrement />
            <NumberFieldInput />
            <NumberFieldIncrement />
          </NumberFieldContent>
        </NumberField>
      </div>
      <div class="grid gap-1.5">
        <header class="text-2xs tracking-wide uppercase">
          {{ t("components.inputs.overpressure.label") }}
        </header>
        <NumberField
          v-model="overpressure.value.value"
          class="grow"
          :step="0.1"
          :min="0"
          :max="20"
        >
          <NumberFieldContent>
            <NumberFieldDecrement />
            <NumberFieldInput />
            <NumberFieldIncrement />
          </NumberFieldContent>
        </NumberField>
      </div>
    </div>

    <Button
      :disabled="isSubmitting || (!temperature.isDirty.value && !overpressure.isDirty.value)"
      class="mt-6"
      @click="submit"
    >
      <RiLoader2Line
        v-if="isSubmitting"
        class="animate-spin"
      />
      <RiSendPlaneLine v-else />
    </Button>

    <div
      v-if="error"
      class="mt-3 text-red-500"
    >
      {{ error }}
    </div>
  </div>
</template>
