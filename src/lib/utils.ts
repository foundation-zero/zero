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

// https://stackoverflow.com/questions/38552003/how-to-decode-jwt-token-in-javascript-without-using-a-library
export function parseJwt<T>(token: string) {
  const base64Url = token.split(".")[1];
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const jsonPayload = decodeURIComponent(
    window
      .atob(base64)
      .split("")
      .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join(""),
  );

  return JSON.parse(jsonPayload) as T;
}
