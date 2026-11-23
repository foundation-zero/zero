import { durationParts } from "@/modules/thrapp/monitoring/monitoring.utils";

/** Two decimals at most, as the Grafana Live tables. */
export function formatReading(value: number | null, unit?: string | null): string {
  if (value === null) return "–";
  const number = value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return unit ? `${number} ${unit}` : number;
}

/** The largest whole unit of an age: "12 s", "5 min", "3 h", "2 d". */
export function formatAge(ageMs: number): string {
  const { days, hours, minutes, seconds } = durationParts(Math.max(0, ageMs) / 1000);
  if (days) return `${days} d`;
  if (hours) return `${hours} h`;
  if (minutes) return `${minutes} min`;
  return `${seconds} s`;
}
