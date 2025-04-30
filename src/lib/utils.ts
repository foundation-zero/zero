import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { computed, Ref } from "vue";

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

export const randomHumidity = () => (30 + Math.random() * 40).toFixed(0);
