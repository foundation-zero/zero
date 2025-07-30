import {
  ControlType,
  ControlTypeMap,
  Room,
  RoomControl,
  RoomSensor,
  RoomState,
  SafeRangeThresholds,
  SensorType,
  SensorTypeMap,
  Thresholds,
  TimeValueObject,
  TimeValueTuple,
  ValidationStatus,
  ValueObject,
} from "@/@types";
import { ArgumentsType, useIntervalFn } from "@vueuse/core";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { computed, ComputedRef, ref, Ref, watch } from "vue";
import { CO2_THRESHOLDS, DEMO_MODE, HUMIDITY_THRESHOLDS, TEMPERATURE_THRESHOLDS } from "./consts";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const isDefined = <T>(value: T | undefined | null): value is T =>
  value !== undefined && value !== null;

export const compareByName = <T extends { name: string }>(a: T, b: T) =>
  a.name.localeCompare(b.name);

export const validationStatusToNumber: Record<ValidationStatus, number> = {
  [ValidationStatus.OK]: 0,
  [ValidationStatus.WARN]: 1,
  [ValidationStatus.FAIL]: 2,
  [ValidationStatus.UNKNOWN]: 0,
};

export const compareByValidationStatus = (a: ValidationStatus, b: ValidationStatus) =>
  validationStatusToNumber[a] - validationStatusToNumber[b];

export const updateSetpointWhenControlsHaveChanged = <T extends RoomControl>(
  value: Ref<number>,
  controls: Ref<T[]>,
) =>
  watch(controls, ([next], [prev]) => {
    if (next?.value !== prev?.value && next !== undefined) {
      value.value = next.value;
    }
  });

export const ratioAsPercentage = (ratio: Ref<number>) =>
  computed({
    get() {
      return ratio.value * 100;
    },
    set(percentage: number) {
      ratio.value = percentage / 100;
    },
  });

export const valueWithValidation = <T>(val: Ref<T>, validateFn: (next: T) => boolean) =>
  computed({
    get() {
      return val.value;
    },
    set(next: T) {
      if (validateFn(next)) {
        val.value = next;
      }
    },
  });

export const valueAsArray = <T>(value: Ref<T>) =>
  computed({
    get() {
      return [value.value];
    },
    set(next: T[]) {
      if (next.length === 0) throw new Error("Array cannot be empty");

      value.value = next[0];
    },
  });

export const formatNumber =
  (digits: number) =>
  (value: number, locale: string = "en-US") => {
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }).format(value);
  };

export const formatInt = formatNumber(0);

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

export const sortByTime = <T extends TimeValueTuple<unknown> | TimeValueObject<unknown>>(
  a: T,
  b: T,
): number => {
  if (Array.isArray(a) && Array.isArray(b)) return a[0].getTime() - b[0].getTime();
  else if ("time" in a && "time" in b) return a.time.getTime() - b.time.getTime();
  return 0;
};

export const useTransform = <T>(
  values: Ref<number[]>,
  transformFn: (val: number, index: number) => T,
): ComputedRef<T[]> => computed(() => values.value.map(transformFn));

export const toValueObject = <T>(value: T): ValueObject<T> => ({ value });
export const toTimeValueObject = <T>([time, value]: TimeValueTuple<T>): TimeValueObject<T> => ({
  time,
  value,
});
export const toTimeValueTuple = <T>(value: TimeValueObject<T>): TimeValueTuple<T> => [
  new Date(value.time),
  value.value,
];

export const validateSafeRange = (
  thresholds: SafeRangeThresholds,
  value?: number,
): ValidationStatus => {
  if (value === undefined || isNaN(value)) {
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

export const validateThreshold = (thresholds: Thresholds, value?: number): ValidationStatus => {
  if (value === undefined || isNaN(value)) {
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

export const isSensorType =
  <T extends SensorType>(type: T) =>
  (sensor: RoomSensor): sensor is SensorTypeMap[T] =>
    sensor.type === type;

export const isControlType =
  <T extends ControlType>(type: T) =>
  (control: RoomControl): control is ControlTypeMap[T] =>
    control.type === type;

export const isLightControl = isControlType(ControlType.LIGHT);
export const isBlindsControl = isControlType(ControlType.BLIND);
export const isTemperatureControl = isControlType(ControlType.TEMPERATURE);
export const isHumidityControl = isControlType(ControlType.HUMIDITY);
export const isCO2Control = isControlType(ControlType.CO2);
export const isAmplifierControl = isControlType(ControlType.AMPLIFIER);

export const isPresenceSensor = isSensorType(SensorType.PRESENCE);
export const isTemperatureSensor = isSensorType(SensorType.TEMPERATURE);
export const isHumiditySensor = isSensorType(SensorType.HUMIDITY);
export const isCO2Sensor = isSensorType(SensorType.CO2);

export const extractActualSensorValue =
  <T extends SensorType>(type: T) =>
  (room: Room) => {
    const value = room.roomsSensors.find(isSensorType(type))?.value;
    if (value !== undefined) return Number(value);
  };

export const extractActualControlValue =
  <T extends ControlType>(type: T) =>
  (room: Room) => {
    const value = room.roomsControls.find(isControlType(type))?.value;
    if (value !== undefined) return Number(value);
  };

export const extractActualHumidity = extractActualSensorValue(SensorType.HUMIDITY);
export const extractActualTemperature = extractActualSensorValue(SensorType.TEMPERATURE);
export const extractActualCO2 = extractActualSensorValue(SensorType.CO2);
export const extractActualPresence = extractActualSensorValue(SensorType.PRESENCE);

export const extractTemperatureSetpoint = extractActualControlValue(ControlType.TEMPERATURE);
export const extractAmplifierStatus = extractActualControlValue(ControlType.AMPLIFIER);
export const extractHumiditySetpoint = extractActualControlValue(ControlType.HUMIDITY);
export const extractCO2Setpoint = extractActualControlValue(ControlType.CO2);
