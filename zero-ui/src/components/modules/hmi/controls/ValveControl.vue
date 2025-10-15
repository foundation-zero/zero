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
import { THRSModules } from "@/lib/consts";
import { toUpperCamelCase } from "@/lib/utils";
import { controlValuesForm, MutationType } from "@/stores/thrs";
import { Loader2Icon, SendIcon } from "lucide-vue-next";
import { toRef } from "vue";

const props = defineProps<{
  controlValues: {
    setpoint: Stamped<number>;
  };
  controlValuesQuery: string;
  componentName: string;
  yardTag: string;
  valveType: string;
  module: keyof THRSModules;
}>();
const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const controlValues = toRef(props, "controlValues");

const { submit, isSubmitting, error, setpoint } = controlValuesForm(
  props.module,
  MutationType.Control,
  "ValveInputType!",
  props.componentName,
  controlValues,
  ["setpoint"],
  props.controlValuesQuery,
  emit,
);
</script>
<template>
  <div class="bg-background flex flex-col rounded-md border p-4 shadow-md">
    <h3 class="overflow-hidden font-semibold text-ellipsis whitespace-nowrap capitalize">
      {{ toUpperCamelCase(componentName) }}
    </h3>
    <p class="text-muted-foreground text-xs">{{ yardTag }} / {{ valveType }}</p>
    <div class="mt-6 grid gap-1.5">
      <header class="text-2xs tracking-wide uppercase">Setpoint</header>
      <div class="flex items-center gap-2">
        <NumberField
          v-model="setpoint.value.value"
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
          :disabled="isSubmitting || !setpoint.isDirty.value"
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
