<script setup lang="ts" generic="K extends keyof ThrsModules">
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { controlValuesForm, MutationType } from "@/modules/thrsim/stores/thrs";
import { ParametersType } from "@/modules/thrsim/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { RiLoader2Line, RiSendPlaneLine } from "@remixicon/vue";

const props = defineProps<{
  componentName: string;
  query: string;
  module: K;
  componentType: ParametersType;
}>();

const modelValue = defineModel<boolean>({
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
  "Boolean!",
  props.componentName,
  modelValue,
  ["value"],
  props.query,
  emit,
);
</script>
<template>
  <div class="bg-background rounded-md border p-4 shadow-md">
    <h3 class="flex items-center justify-between font-semibold capitalize">
      <label
        :for="`${componentName}-on`"
        class="overflow-hidden text-ellipsis whitespace-nowrap"
        >{{ toUpperCamelCase(componentName) }}</label
      >
      <Switch
        :id="`${componentName}-on`"
        v-model:model-value="value"
      />
    </h3>

    <Button
      :disabled="isSubmitting || !isDirty"
      class="mt-3 w-full"
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
