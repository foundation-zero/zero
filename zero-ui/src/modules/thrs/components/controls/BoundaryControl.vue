<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import { THRSModules } from "@/modules/thrs/lib/consts";
import { controlValuesForm, MutationType } from "@/modules/thrs/stores/thrs";
import { BoundarySimulation } from "@/modules/thrs/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { Loader2Icon, SendIcon } from "lucide-vue-next";
import { toRef } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  values: BoundarySimulation;
  componentName: string;
  query: string;
  module: keyof THRSModules;
}>();
const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const controlValues = toRef(props, "values");

const { submit, isSubmitting, error, flow, temperature } = controlValuesForm(
  props.module,
  MutationType.Simulation,
  "BoundaryInputType!",
  props.componentName,
  controlValues,
  ["flow", "temperature"],
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

    <div class="mt-6 grid grid-cols-2 gap-x-2">
      <div class="grid gap-1.5">
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
    </div>

    <Button
      :disabled="isSubmitting || (!flow.isDirty.value && !temperature.isDirty.value)"
      class="mt-6"
      @click="submit"
    >
      <Loader2Icon
        v-if="isSubmitting"
        class="animate-spin"
      />
      <SendIcon v-else />
    </Button>

    <div
      v-if="error"
      class="mt-3 text-red-500"
    >
      {{ error }}
    </div>
  </div>
</template>
