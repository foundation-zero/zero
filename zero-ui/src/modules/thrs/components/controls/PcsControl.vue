<script setup lang="ts" generic="K extends keyof THRSModules">
import { Button } from "@/components/ui/button";
import Select from "@/components/ui/select/Select.vue";
import SelectContent from "@/components/ui/select/SelectContent.vue";
import SelectItem from "@/components/ui/select/SelectItem.vue";
import SelectTrigger from "@/components/ui/select/SelectTrigger.vue";
import SelectValue from "@/components/ui/select/SelectValue.vue";
import { THRSModules, THRSSimulationType, THRUSTER_MODES } from "@/modules/thrs/lib/consts";
import { controlValuesForm, MutationType } from "@/modules/thrs/stores/thrs";
import { PcsSimulation, SimulationComponentType } from "@/modules/thrs/types";
import { toUpperCamelCase } from "@common/lib/utils";
import { Loader2Icon, SendIcon } from "lucide-vue-next";
import { toRef } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  values: PcsSimulation;
  componentName: string;
  query: string;
  simulation: THRSSimulationType;
  componentType: SimulationComponentType;
}>();

const values = toRef(props, "values");

const emit = defineEmits<{
  (e: "update:controlValues", value: unknown): void;
}>();

const { submit, isSubmitting, error, mode } = controlValuesForm(
  props.simulation,
  MutationType.Simulation,
  "PcsInputType!",
  props.componentName,
  values,
  ["mode"],
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
        {{ t("components.inputs.mode.label") }}
      </header>
      <div class="grid gap-6">
        <Select v-model="mode.value.value">
          <SelectTrigger class="border-border w-full capitalize">
            <SelectValue
              class="capitalize"
              placeholder="Select a mode"
            >
              <span class="capitalize">{{ mode.value.value.toLocaleLowerCase() }}</span>
            </SelectValue>
          </SelectTrigger>
          <SelectContent class="capitalize">
            <SelectItem
              v-for="propMode in THRUSTER_MODES"
              :key="propMode"
              :value="propMode"
              >{{ propMode.toLocaleLowerCase() }}</SelectItem
            >
          </SelectContent>
        </Select>
        <Button
          :disabled="isSubmitting || !mode.isDirty.value"
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
