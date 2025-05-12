import { SafeRangeThresholds, Thresholds, ValidationStatus, ValueObject } from "@/@types";
import { useIntervalFn } from "@vueuse/core";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { computed, ComputedRef, ref, Ref } from "vue";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const isDefined = <T>(value: T | undefined | null): value is T =>
  value !== undefined && value !== null;

export const compareByName = <T extends { name: string }>(a: T, b: T) =>
  a.name.localeCompare(b.name);

export const ratioAsPercentage = (ratio: Ref<number>) =>
  computed({
    get() {
      return ratio.value * 100;
    },
    set(percentage: number) {
      ratio.value = percentage / 100;
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
  new Array(amount).fill(0).map(() => Math.floor(Math.random() * (max - min + 1) + min));

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

export const useTransform = <T>(
  values: Ref<number[]>,
  transformFn: (val: number) => T,
): ComputedRef<T[]> => computed(() => values.value.map(transformFn));

export const toValueObject = <T>(value: T): ValueObject<T> => ({ value });

export const useSafeRange = (
  thresholds: SafeRangeThresholds,
  value: Ref<number>,
): Ref<ValidationStatus> =>
  computed(() => {
    if (value.value < thresholds[0] || value.value > thresholds[1]) {
      return ValidationStatus.WARN;
    }

    return ValidationStatus.OK;
  });

export const useThresholds = (thresholds: Thresholds, value: Ref<number>): Ref<ValidationStatus> =>
  computed(() => {
    if (value.value >= thresholds[1]) {
      return ValidationStatus.FAIL;
    } else if (value.value >= thresholds[0]) {
      return ValidationStatus.WARN;
    } else {
      return ValidationStatus.OK;
    }
  });
