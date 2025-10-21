<script setup lang="ts" generic="K extends keyof THRSModules">
import { ParametersType } from "@/@types/thrs";
import { Button } from "@/components/ui/shadcn/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/shadcn/number-field";
import { THRSModules } from "@/lib/consts";
import { toUpperCamelCase } from "@/lib/utils";
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

const modelValue = defineModel<number>({
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
  "Float!",
  props.componentName,
  modelValue,
  ["value"],
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
        {{ t(`components.inputs.${componentType}.label`) }}
        <span class="text-muted-foreground ml-0.5">{{
          t(`components.inputs.${componentType}.unit`)
        }}</span>
      </header>
      <div class="flex items-center gap-2">
        <NumberField
          v-model="value"
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
          :disabled="isSubmitting || !isDirty"
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
