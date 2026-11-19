import type { BadgeVariants } from "@/components/ui/badge";
import type { AlarmPriority } from "../../types";

export const PRIORITY_BADGE: Record<AlarmPriority, BadgeVariants["variant"]> = {
  GEA: "destructive",
  EMERGENCY: "destructive",
  ALARM: "destructive",
  WARNING: "warning",
  UNKNOWN: "warning",
  CAUTION: "secondary",
  EVENT: "outline",
};
