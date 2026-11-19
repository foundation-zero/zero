export type AlarmPriority =
  | "GEA"
  | "EMERGENCY"
  | "ALARM"
  | "WARNING"
  | "CAUTION"
  | "EVENT"
  | "UNKNOWN";

export type AlarmUpdate =
  | "ACTIVATED"
  | "ACKNOWLEDGED"
  | "IDLE"
  | "INHIBITED"
  | "INVALID"
  | "UNBOUND"
  | "EVENT"
  | "UNKNOWN";

/** One AMCS alarm, as zero-alert-forwarder folds it from the rows of its updates. */
export interface Alarm {
  system: string | null;
  tag: string | null;
  location: string | null;
  description: string | null;
  priority: AlarmPriority | null;
  active: boolean | null;
  acknowledged: boolean | null;
  /** Unknown when the alarm was raised before the forwarder started reading. */
  activatedAt: string | null;
  lastChangeAt: string | null;
  lastUpdate: AlarmUpdate | null;
}

export interface AlarmList {
  publishedAt: string | null;
  recentWindowMinutes: number | null;
  alarms: (Alarm | null)[] | null;
}

/** The list is `null` when the forwarder stopped publishing it. */
export type AlarmListQueryResponse = { alerts: { alarmList: AlarmList | null } | null };
