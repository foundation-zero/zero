export type ReferenceThresholds = {
  warningLow: number;
  warningHigh: number;
  alarmLow: number;
  alarmHigh: number;
  target: number;
};

export const enum VariableType {
  Percentage = "percentage",
  Tonnes = "tonnes",
}

export const enum VariableState {
  Neutral = "neutral",
  Warning = "warning",
  Alarm = "alarm",
  Unknown = "unknown",
}
