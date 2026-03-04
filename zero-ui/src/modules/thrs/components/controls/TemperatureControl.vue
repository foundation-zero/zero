<script setup lang="ts" generic="K extends keyof ThrsModules">
import { Button } from "@/components/ui/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import { ThrsModules, ThrsSimulationType } from "@/modules/thrs/lib/consts";
import { controlValuesForm, MutationType } from "@/modules/thrs/stores/thrs";
import { SimulationComponentType, TemperatureSimulation } from "@/modules/thrs/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { Loader2Icon, SendIcon } from "lucide-vue-next";
import { toRef } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  values: TemperatureSimulation;
  componentName: string;
  query: string;
  simulation: ThrsSimulationType;
  componentType: SimulationComponentType;
}>();

const values = toRef(props, "values");

const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const { submit, isSubmitting, error, temperature } = controlValuesForm(
  props.simulation,
  MutationType.Simulation,
  "TemperatureBoundaryInputType!",
  props.componentName,
  values,
  ["temperature"],
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
        {{ t("components.inputs.temperature.label") }}
      </header>
      <div class="grid gap-6">
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

        <Button
          :disabled="isSubmitting || !temperature.isDirty.value"
          @click="submit"
        >
          <Loader2Icon
            v-if="isSubmitting"
            class="animate-spin"
          />
          <SendIcon v-else />
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
