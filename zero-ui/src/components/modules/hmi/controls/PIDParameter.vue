<script setup lang="ts" generic="K extends keyof THRSModules">
import { ParametersType, PID } from "@/@types/thrs";
import { Button } from "@/components/ui/shadcn/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/shadcn/number-field";
import NumberFieldPrefix from "@/components/ui/shadcn/number-field/NumberFieldPrefix.vue";
import { THRSModules } from "@/lib/consts";
import { toElementRefs, toUpperCamelCase } from "@/lib/utils";
import { controlValuesForm, MutationType } from "@/stores/thrs";
import { Loader2Icon, SendIcon } from "lucide-vue-next";

import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  componentName: string;
  query: string;
  module: K;
  componentType: ParametersType;
}>();

const modelValue = defineModel<PID>({
  required: true,
});

const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const {
  submit,
  isSubmitting,
  error,
  value: { value, isDirty },
} = controlValuesForm(
  props.module,
  MutationType.Parameter,
  "[Float!]!",
  props.componentName,
  modelValue,
  ["value"],
  props.query,
  emit,
);

const [p, i, d] = toElementRefs(value);
</script>

<template>
  <div class="bg-background flex flex-col rounded-md border p-4 shadow-md">
    <h3 class="overflow-hidden font-semibold text-ellipsis whitespace-nowrap capitalize">
      {{ toUpperCamelCase(componentName) }}
    </h3>

    <div class="mt-6 grid gap-1.5">
      <header class="text-2xs tracking-wide uppercase">{{ componentType }}</header>

      <NumberField
        v-model="p"
        :step="0.001"
        :min="0"
        :max="1"
      >
        <NumberFieldContent>
          <NumberFieldPrefix>{{ t("components.inputs.pid.p") }}</NumberFieldPrefix>
          <NumberFieldDecrement class="left-8.5" />
          <NumberFieldInput />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>

      <NumberField
        v-model="i"
        :step="0.01"
        :min="-1"
        :max="1"
      >
        <NumberFieldContent>
          <NumberFieldPrefix>{{ t("components.inputs.pid.i") }}</NumberFieldPrefix>
          <NumberFieldDecrement class="left-8.5" />
          <NumberFieldInput />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>

      <NumberField
        v-model="d"
        :step="0.001"
        :min="0"
        :max="1"
      >
        <NumberFieldContent>
          <NumberFieldPrefix>{{ t("components.inputs.pid.d") }}</NumberFieldPrefix>
          <NumberFieldDecrement class="left-8.5" />
          <NumberFieldInput />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>

      <Button
        :disabled="isSubmitting || !isDirty"
        class="mt-3"
        @click="submit"
      >
        <Loader2Icon
          v-if="isSubmitting"
          class="animate-spin"
        />
        <SendIcon v-else />
      </Button>
    </div>

    <div
      v-if="error"
      class="mt-3 text-red-500"
    >
      {{ error }}
    </div>
  </div>
</template>
