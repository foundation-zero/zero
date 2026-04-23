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
import { HeatSourceSimulation } from "@/modules/thrs/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { RiLoader2Line, RiSendPlaneLine } from "@remixicon/vue";
import { toRef } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  values: HeatSourceSimulation;
  componentName: string;
  query: string;
  simulation: ThrsSimulationType;
}>();

const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const values = toRef(props, "values");

const { submit, isSubmitting, error, heatFlow } = controlValuesForm(
  props.simulation,
  MutationType.Simulation,
  "HeatSourceInputType!",
  props.componentName,
  values,
  ["heatFlow"],
  props.query,
  emit,
);
</script>

<template>
  <div class="bg-background flex flex-col rounded-md border p-4 shadow-md">
    <h3 class="overflow-hidden font-semibold text-ellipsis whitespace-nowrap capitalize">
      {{ toUpperCamelCase(componentName) }}
    </h3>

    <div class="mt-6 grid gap-1.5">
      <header class="text-2xs tracking-wide uppercase">
        {{ t("components.inputs.heatFlow.label") }}
      </header>
      <div class="grid gap-6">
        <NumberField
          v-model="heatFlow.value.value"
          class="grow"
          :step="1"
          :min="0"
          :max="10000"
        >
          <NumberFieldContent>
            <NumberFieldDecrement />
            <NumberFieldInput />
            <NumberFieldIncrement />
          </NumberFieldContent>
        </NumberField>

        <Button
          :disabled="isSubmitting || !heatFlow.isDirty.value"
          @click="submit"
        >
          <RiLoader2Line
            v-if="isSubmitting"
            class="animate-spin"
          />
          <RiSendPlaneLine v-else />
        </Button>
      </div>
    </div>

    <div
      v-if="error"
      class="mt-3 text-red-500"
    >
      {{ error }}
    </div>
  </div>
</template>
