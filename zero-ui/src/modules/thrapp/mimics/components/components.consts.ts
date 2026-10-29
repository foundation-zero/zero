export const enum ComponentOrientation {
  Up = 0,
  UpRight = 45,
  Right = 90,
  DownRight = 135,
  Down = 180,
  DownLeft = 225,
  Left = 270,
  UpLeft = 315,
}

export const enum HeatingState {
  HeatingHigh = "heating-high",
  HeatingMedium = "heating-medium",
  HeatingLow = "heating-low",
  CoolingHigh = "cooling-high",
  CoolingMedium = "cooling-medium",
  CoolingLow = "cooling-low",
  Active = "active",
  Inactive = "inactive",
  Idle = "idle",
}

export const HEATING_STATE_COLORS: Record<HeatingState, string> = {
  [HeatingState.HeatingHigh]: "var(--heating-high)",
  [HeatingState.HeatingMedium]: "var(--heating-medium)",
  [HeatingState.HeatingLow]: "var(--heating-low)",
  [HeatingState.CoolingHigh]: "var(--cooling-high)",
  [HeatingState.CoolingMedium]: "var(--cooling-medium)",
  [HeatingState.CoolingLow]: "var(--cooling-low)",
  [HeatingState.Active]: "var(--attention)",
  [HeatingState.Inactive]: "var(--attention-dull)",
  [HeatingState.Idle]: "var(--disabled)",
};

export const CLOCKWISE_ORIENTATIONS = [
  ComponentOrientation.Up,
  ComponentOrientation.UpRight,
  ComponentOrientation.Right,
  ComponentOrientation.DownRight,
  ComponentOrientation.Down,
  ComponentOrientation.DownLeft,
  ComponentOrientation.Left,
  ComponentOrientation.UpLeft,
];

export const enum MimicComponentState {
  Normal = "normal",
  Alarm = "alarm",
  Manual = "manual",
}

export const stateColorMap: Record<MimicComponentState, string> = {
  [MimicComponentState.Normal]: "var(--attention)",
  [MimicComponentState.Alarm]: "var(--destructive)",
  [MimicComponentState.Manual]: "var(--warning)",
};
