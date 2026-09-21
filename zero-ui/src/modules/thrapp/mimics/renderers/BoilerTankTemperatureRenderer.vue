<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { BoilerTankState, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { computed, toRef } from "vue";
import { FieldRendererProps } from ".";
import { getFieldValue, getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  FieldRendererProps<BoilerTankState> & {
    temperature: ModuleField<SensorComponentType.Temperature>;
    minimumTemperature: ModuleField<ParametersType.Temperature>;
  }
>();

const t = tScoped("thrapp.mimics.boilerTank.modes");
const value = getFieldValue(toRef(props, "value"));
const { getSensorValue, getParameter } = getMimicDataProvider();
const temperature = getSensorValue(props.temperature);
const minimumTemperature = getParameter(props.minimumTemperature);

const mode = computed(() => {
  const currentTemperature = temperature.value?.temperature.value ?? 0;
  const minTemperature = minimumTemperature.value ?? 0;
  const mode = value.value;

  if (!currentTemperature || !minTemperature) return undefined;
  else if (currentTemperature >= minTemperature) return BoilerTankState.OnTemperature;
  else if (mode === BoilerTankState.Boosting) return BoilerTankState.Boosting;
  else return BoilerTankState.NeedsBoost;
});
</script>

<template>
  <span v-if="mode">{{ t(mode) }}</span>
  <span v-else>-</span>
</template>
