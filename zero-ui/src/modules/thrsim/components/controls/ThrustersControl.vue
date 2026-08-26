<script setup lang="ts" generic="K extends keyof ThrsModules">
import { Button } from "@/components/ui/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import { Switch } from "@/components/ui/switch";
import { ThrsModules, ThrsSimulationType } from "@/modules/thrsim/lib/consts";
import { controlValuesForm, MutationType } from "@/modules/thrsim/stores/thrs";
import { ThrusterSimulation } from "@/modules/thrsim/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { RiLoader2Line, RiSendPlaneLine } from "@remixicon/vue";
import { toRef } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  values: ThrusterSimulation;
  componentName: string;
  query: string;
  simulation: ThrsSimulationType;
}>();
const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const controlValues = toRef(props, "values");

const { submit, isSubmitting, error, active, heatFlow } = controlValuesForm(
  props.simulation,
  MutationType.Simulation,
  "ThrusterInputType!",
  props.componentName,
  controlValues,
  ["active", "heatFlow"],
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
      <Switch
        :id="`${componentName}-on`"
        v-model:model-value="active.value.value"
      />
    </h3>

    <div class="mt-6 grid gap-1.5">
      <header class="text-2xs tracking-wide uppercase">
        {{ t("components.inputs.thruster.label") }}
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
          :disabled="isSubmitting || (!heatFlow.isDirty.value && !active.isDirty.value)"
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
