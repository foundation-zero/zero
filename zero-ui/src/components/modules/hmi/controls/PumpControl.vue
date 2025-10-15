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
import { Switch } from "@/components/ui/shadcn/switch";
import { THRSModules } from "@/lib/consts";
import { toUpperCamelCase } from "@/lib/utils";
import { controlValuesForm, MutationType } from "@/stores/thrs";
import { Loader2Icon, SendIcon } from "lucide-vue-next";
import { toRef } from "vue";

const props = defineProps<{
  controlValues: {
    dutypoint: Stamped<number>;
    on: Stamped<boolean>;
  };
  componentName: string;
  yardTag: string;
  controlValuesQuery: string;
  module: keyof THRSModules;
}>();
const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const controlValues = toRef(props, "controlValues");

const { submit, isSubmitting, error, dutypoint, on } = controlValuesForm(
  props.module,
  MutationType.Control,
  "PumpInputType!",
  props.componentName,
  controlValues,
  ["dutypoint", "on"],
  props.controlValuesQuery,
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
        v-model:model-value="on.value.value"
      />
    </h3>
    <p class="text-muted-foreground text-xs">{{ yardTag }}</p>

    <div class="mt-6 grid gap-1.5">
      <header class="text-2xs tracking-wide uppercase">Speed</header>
      <div class="flex items-center gap-3">
        <NumberField
          v-model="dutypoint.value.value"
          class="grow"
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

        <Button
          :disabled="isSubmitting || (!dutypoint.isDirty.value && !on.isDirty.value)"
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
