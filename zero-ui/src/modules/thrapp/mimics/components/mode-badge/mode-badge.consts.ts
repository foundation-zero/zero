import { BoilerTankState } from "@/modules/thrapp/types/thrs";

export const enum ModeBadgeMode {
  Idle = "Idle",

  AlwaysActive = "AlwaysActive",
  Active = "Active",
  Using = "Using",

  CoolingLow = "CoolingLow",
  Cooling = "Cooling",
  CoolingHigh = "CoolingHigh",

  ManualControl = "ManualControl",
  AdvisoryOff = "AdvisoryOff",
  Disabled = "Disabled",

  BoostingLow = "BoostingLow",
  Boosting = "Boosting",
  BoostingHigh = "BoostingHigh",

  FillingLow = "FillingLow",
  Filling = "Filling",
}

export const enum ModeBadgeSize {
  Asset = "asset",
  Circuit = "circuit",
  Tank = "tank",
  Navigation = "navigation",
}

export const SIZE_ATTRIBUTES: Record<ModeBadgeSize, string> = {
  [ModeBadgeSize.Asset]: "rounded-lg px-4 py-0.5 text-xs",
  [ModeBadgeSize.Tank]: "rounded-lg px-4 py-0.5 text-xs",
  [ModeBadgeSize.Circuit]: "rounded-xl px-4 py-0.5 text-sm",
  [ModeBadgeSize.Navigation]: "rounded-xl px-3 py-2 text-base leading-4",
};

export const MODE_COLORS: Record<ModeBadgeMode, string> = {
  [ModeBadgeMode.Idle]: "var(--muted-foreground)",
  [ModeBadgeMode.Active]: "var(--constructive)",
  [ModeBadgeMode.AlwaysActive]: "var(--constructive)",
  [ModeBadgeMode.Using]: "var(--flows-use-medium)",
  [ModeBadgeMode.CoolingLow]: "var(--cooling-low)",
  [ModeBadgeMode.Cooling]: "var(--cooling-medium)",
  [ModeBadgeMode.CoolingHigh]: "var(--cooling-high)",
  [ModeBadgeMode.BoostingLow]: "var(--heating-low)",
  [ModeBadgeMode.Boosting]: "var(--heating-medium)",
  [ModeBadgeMode.BoostingHigh]: "var(--heating-high)",
  [ModeBadgeMode.FillingLow]: "var(--flows-fill-low)",
  [ModeBadgeMode.Filling]: "var(--flows-fill-medium)",
  [ModeBadgeMode.ManualControl]: "var(--warning)",
  [ModeBadgeMode.AdvisoryOff]: "var(--brand-muted)",
  [ModeBadgeMode.Disabled]: "var(--destructive-muted)",
};

export const DHW_BOOSTING_MODE_MODES: Record<string, ModeBadgeMode> = {
  idle: ModeBadgeMode.Idle,
  boosting_low_temperature: ModeBadgeMode.BoostingLow,
  boosting_high_temperature: ModeBadgeMode.Boosting,
  boosting_heatpump: ModeBadgeMode.BoostingHigh,
};

export const DHW_FILLING_MODE_MODES: Record<string, ModeBadgeMode> = {
  idle: ModeBadgeMode.Idle,
  filling: ModeBadgeMode.Filling,
};

export const DHW_TANK_STATE_MODES: Record<BoilerTankState, ModeBadgeMode> = {
  [BoilerTankState.InUse]: ModeBadgeMode.Using,
  [BoilerTankState.Boosting]: ModeBadgeMode.Boosting,
  [BoilerTankState.Standby]: ModeBadgeMode.Idle,
  [BoilerTankState.Disabled]: ModeBadgeMode.Disabled,
  [BoilerTankState.Filling]: ModeBadgeMode.Filling,
  [BoilerTankState.NeedsBoost]: ModeBadgeMode.BoostingLow,
  [BoilerTankState.NeedsFill]: ModeBadgeMode.FillingLow,
  [BoilerTankState.OnTemperature]: ModeBadgeMode.Idle,
};
