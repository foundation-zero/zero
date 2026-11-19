import { format, isSameDay } from "date-fns";

/** The time of day, with the date only when it is not on the day of `now`. */
export function formatAlarmTime(timestamp: string | null, now: Date = new Date()): string {
  if (!timestamp) {
    return "—";
  }
  const date = new Date(timestamp);
  return format(date, isSameDay(date, now) ? "HH:mm:ss" : "d MMM HH:mm:ss");
}
