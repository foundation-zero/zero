import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { computed, Ref } from "vue";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const isDefined = <T>(value: T | undefined | null): value is T =>
  value !== undefined && value !== null;

export const ratioAsPercentage = (ratio: Ref<number>) =>
  computed({
    get() {
      return ratio.value * 100;
    },
    set(percentage: number) {
      ratio.value = percentage / 100;
    },
  });
