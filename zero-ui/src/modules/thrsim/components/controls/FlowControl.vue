<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import { controlValuesForm, MutationType } from "@/modules/thrsim/stores/thrs";
import { FlowSimulation } from "@/modules/thrsim/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { RiLoader2Line, RiSendPlaneLine } from "@remixicon/vue";
import { toRef } from "vue";
import { useI18n } from "vue-i18n";
import { ThrsSimulationType } from "../../lib/consts";

const { t } = useI18n();

const props = defineProps<{
  values: FlowSimulation;
  componentName: string;
  query: string;
  simulation: ThrsSimulationType;
}>();
const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const controlValues = toRef(props, "values");

const { submit, isSubmitting, error, flow } = controlValuesForm(
  props.simulation,
  MutationType.Simulation,
  "BoundaryInputType!",
  props.componentName,
  controlValues,
  ["flow"],
  props.query,
  emit,
);
</script>
<template>
  <div class="bg-background flex flex-col rounded-md border p-4 shadow-md">
    <h3 class="flex items-center justify-between font-semibold capitalize">
      <label
        :for="`${componentName}-on`"
        class="overflow-hidden text-ellipsis whitespace-nowrap"
        >{{ toUpperCamelCase(componentName) }}</label
      >
    </h3>

    <div class="mt-6 grid gap-1.5">
      <header class="text-2xs tracking-wide uppercase">
        {{ t("components.inputs.flow.label") }}
      </header>
      <NumberField
        v-model="flow.value.value"
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

    <Button
      :disabled="isSubmitting || !flow.isDirty.value"
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
