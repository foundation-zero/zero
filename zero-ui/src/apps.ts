import { ENV } from "./settings";

export const enum ZeroApps {
  "heatSimulation" = "heatSimulation",
  "heat" = "heat",
  "loads" = "loads",
  "grafana" = "grafana",
  "domestic" = "domestic",
  "sailSystem" = "sailSystem",
  "powerTags" = "powerTags",
}

const DEFAULT_INCLUDED_APPS: ZeroApps[] = [ZeroApps.loads, ZeroApps.heat, ZeroApps.domestic];

const VALID_APPS = new Set<ZeroApps>([
  ZeroApps.heatSimulation,
  ZeroApps.heat,
  ZeroApps.loads,
  ZeroApps.grafana,
  ZeroApps.domestic,
  ZeroApps.sailSystem,
  ZeroApps.powerTags,
]);

const APP_ALIASES: Record<string, ZeroApps> = {
  heatSystem: ZeroApps.heat,
  heatSystemSimulation: ZeroApps.heatSimulation,
  thrs: ZeroApps.heat,
  thrsim: ZeroApps.heatSimulation,
};

const envIncludedApps = String(ENV.VITE_INCLUDE_APPS)
  .split(",")
  .map((app) => APP_ALIASES[app.trim()] ?? app.trim())
  .filter((s): s is ZeroApps => VALID_APPS.has(s as ZeroApps));

export const INCLUDED_APPS: ZeroApps[] = envIncludedApps.length
  ? [...new Set(envIncludedApps)]
  : DEFAULT_INCLUDED_APPS;
