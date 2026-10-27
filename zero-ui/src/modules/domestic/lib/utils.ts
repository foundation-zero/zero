import { ArgumentsType, useIntervalFn } from "@vueuse/core";
import { Maybe } from "graphql/jsutils/Maybe";
import { computed, ComputedRef, ref, Ref, watch } from "vue";
import {
  Room,
  RoomState,
  SafeRangeThresholds,
  Thresholds,
  TimeValueTuple,
  ValidationStatus,
} from "../types";
import { CO2_THRESHOLDS, DEMO_MODE, HUMIDITY_THRESHOLDS, TEMPERATURE_THRESHOLDS } from "./consts";

export const validationStatusToNumber: Record<ValidationStatus, number> = {
  [ValidationStatus.OK]: 0,
  [ValidationStatus.WARN]: 1,
  [ValidationStatus.FAIL]: 2,
  [ValidationStatus.UNKNOWN]: 0,
};

export const compareByValidationStatus = (a: ValidationStatus, b: ValidationStatus) =>
  validationStatusToNumber[a] - validationStatusToNumber[b];

export const generateRandomValues = (amount: number, min: number = 0, max: number = 1000) =>
  new Array(amount).fill(0).map(() => Math.random() * (max - min + 1) + min);

export type LiveValuesOptions = {
  min: number;
  max: number;
  timeout: number;
};

export function useLiveRandomValues(
  amount: number,
  options: Partial<LiveValuesOptions> = {},
): Ref<number[]> {
  const { min = 0, max = 1000, timeout = 5000 } = options;
  const randomValues = ref<number[]>(generateRandomValues(amount, min, max));

  useIntervalFn(() => {
    randomValues.value.shift();
    randomValues.value.push(...generateRandomValues(1, min, max));
  }, timeout);

  return randomValues;
}

const ONE_DAY = 24 * 3600 * 1000;

export const useDemoValues =
  (demoMode: boolean) =>
  <T extends TimeValueTuple<number>>(
    prodValuesFn: () => Ref<T[]>,
    ...args: ArgumentsType<typeof useLiveRandomValues>
  ): Ref<TimeValueTuple<number>[]> =>
    demoMode
      ? useTransform(
          useLiveRandomValues(...args),
          (val, index) => [new Date(Date.now() + index * ONE_DAY), val] as T,
        )
      : prodValuesFn();

export const useDemoControlValues = useDemoValues(DEMO_MODE);
export const useDemoSensorValues = useDemoValues(DEMO_MODE);

export const useTransform = <T>(
  values: Ref<number[]>,
  transformFn: (val: number, index: number) => T,
): ComputedRef<T[]> => computed(() => values.value.map(transformFn));

export const validateSafeRange = (
  thresholds: SafeRangeThresholds,
  value?: number | null,
): ValidationStatus => {
  if (value == undefined || isNaN(value)) {
    return ValidationStatus.UNKNOWN;
  } else if (value < thresholds[0] || value > thresholds[1]) {
    return ValidationStatus.WARN;
  } else {
    return ValidationStatus.OK;
  }
};

export const useSafeRange = (
  thresholds: SafeRangeThresholds,
  value: Ref<number>,
): Ref<ValidationStatus> => computed(() => validateSafeRange(thresholds, value.value));

export const validateThreshold = (
  thresholds: Thresholds,
  value?: number | null,
): ValidationStatus => {
  if (value == undefined || isNaN(value)) {
    return ValidationStatus.UNKNOWN;
  } else if (value >= thresholds[1]) {
    return ValidationStatus.FAIL;
  } else if (value >= thresholds[0]) {
    return ValidationStatus.WARN;
  } else {
    return ValidationStatus.OK;
  }
};

export const useThresholds = (thresholds: Thresholds, value: Ref<number>): Ref<ValidationStatus> =>
  computed(() => validateThreshold(thresholds, value.value));

export const getOverallState = (states: ValidationStatus[]): ValidationStatus => {
  if (states.some((state) => state === ValidationStatus.FAIL)) return ValidationStatus.FAIL;
  else if (states.some((state) => state === ValidationStatus.WARN)) return ValidationStatus.WARN;
  else return ValidationStatus.OK;
};

export const getRoomState = (room: Room): RoomState => {
  const stateCO2 = validateThreshold(CO2_THRESHOLDS, extractActualCO2(room));
  const stateTemperature = validateThreshold(
    TEMPERATURE_THRESHOLDS,
    extractActualTemperature(room),
  );
  const stateHumidity = validateSafeRange(HUMIDITY_THRESHOLDS, extractActualHumidity(room));

  return {
    co2: stateCO2,
    temperature: stateTemperature,
    humidity: stateHumidity,
    overall: getOverallState([stateTemperature, stateHumidity, stateCO2]),
  };
};

export const hasTemperatureControl = (room: Room) => !!room.airConditioning;
export const hasHumidityControl = (room: Room) => !!room.airConditioning;
export const hasCO2Control = (room: Room) => !!room.ventilation;

export const extractActualHumidity = (room: Room) => room.airConditioning?.actualHumidity;
export const extractActualTemperature = (room: Room) => room.airConditioning?.actualTemperature;
export const extractActualCO2 = (room: Room) => room.ventilation?.actualCo2;

export const extractTemperatureSetpoint = (room: Room) => room.airConditioning?.temperatureSetpoint;
export const extractAmplifierStatus = (room: Room) => room.amplifier?.on;
export const extractHumiditySetpoint = (room: Room) => room.airConditioning?.humiditySetpoint;
export const extractCO2Setpoint = (room: Room) => room.ventilation?.co2Setpoint;

export const updateSetpointWhenControlsHaveChanged = <K extends string>(
  value: Ref<Maybe<number>>,
  controls: Ref<{ [key in K]?: Maybe<number> }[]>,
  key: K,
) =>
  watch(controls, ([next], [prev]) => {
    if (next?.[key] !== prev?.[key] && next !== undefined) {
      value.value = next[key];
    }
  });
