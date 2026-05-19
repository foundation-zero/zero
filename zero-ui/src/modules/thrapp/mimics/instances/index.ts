import { useIntervalFn } from "@vueuse/core";
import { MimicComponentBaseProps } from "../components";

import { refValue } from "@/modules/common/lib/utils";
import { computed, MaybeRef, ref } from "vue";
export { default as ActuatedValveInstance } from "./ActuatedValveInstance.vue";
export { default as CheckValveInstance } from "./CheckValveInstance.vue";
export { default as FlowSensorInstance } from "./FlowSensorInstance.vue";
export { default as HeatExchangerInstance } from "./HeatExchangerInstance.vue";
export { default as HeatExchangerLabelInstance } from "./HeatExchangerLabelInstance.vue";
export { default as LevelSensorInstance } from "./LevelSensorInstance.vue";
export { default as LoopCircuitInstance } from "./LoopCircuitInstance.vue";
export { default as ManualValveInstance } from "./ManualValveInstance.vue";
export { default as PipeHeatExchangerInstance } from "./PipeHeatExchangerInstance.vue";
export { default as PressureGaugeInstance } from "./PressureGaugeInstance.vue";
export { default as PressureSensorInstance } from "./PressureSensorInstance.vue";
export { default as PumpInstance } from "./PumpInstance.vue";
export { default as TemperatureSensorInstance } from "./TemperatureSensorInstance.vue";

export type MimicComponentInstanceProps = MimicComponentBaseProps & {
  tagId?: string;
  x: number | string;
  y: number | string;
};

export const useRandomizedValue = <T>(valueFn: () => T, interval = 10_000) => {
  const value = ref<T>(valueFn());

  useIntervalFn(() => (value.value = valueFn()), interval);

  return value;
};

export const useRandomizedState = <T>(possibleValues: T[], interval = 10_000) =>
  useRandomizedValue(
    () => possibleValues[Math.floor(Math.random() * possibleValues.length)],
    interval,
  );

export const useDeltaT = (tIn: MaybeRef<number>, tOut: MaybeRef<number>) =>
  computed(() => refValue(tOut) - refValue(tIn));

export const useRandomizedNumber = (min: number, max: number, interval = 10_000) =>
  useRandomizedValue(() => Math.floor(Math.random() * (max - min + 1)) + min, interval);
