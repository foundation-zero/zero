import type { Alarm } from "../types";

export function isActive(alarm: Pick<Alarm, "active"> | null): boolean {
  return !!alarm?.active;
}
