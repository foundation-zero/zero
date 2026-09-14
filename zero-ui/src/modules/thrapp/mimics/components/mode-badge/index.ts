export { default as ModeBadge } from "./ModeBadge.vue";
export { default as ModeBadges } from "./ModeBadges.vue";

export const enum ModeBadgeMode {
  Idle = "Idle",

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
}

export const SIZE_ATTRIBUTES: Record<ModeBadgeSize, string> = {
  [ModeBadgeSize.Asset]: "rounded-lg py-0.5 text-xs",
  [ModeBadgeSize.Tank]: "rounded-lg py-0.5 text-xs",
  [ModeBadgeSize.Circuit]: "rounded-xl py-1 text-sm",
};

export const MODE_COLORS: Record<ModeBadgeMode, string> = {
  [ModeBadgeMode.Idle]: "var(--muted-foreground)",
  [ModeBadgeMode.Active]: "var(--constructive)",
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
  [ModeBadgeMode.AdvisoryOff]: "var(--destructive)",
  [ModeBadgeMode.Disabled]: "var(--destructive-muted)",
};
