export const enum ZeroApps {
  "thrsim" = "thrsim",
  "thrs" = "thrs",
  "loads" = "loads",
  "grafana" = "grafana",
  "domestic" = "domestic",
  "sailSystem" = "sailSystem",
}

const DEFAULT_INCLUDED_APPS: ZeroApps[] = [ZeroApps.loads, ZeroApps.thrs, ZeroApps.domestic];

const VALID_APPS = new Set<ZeroApps>([
  ZeroApps.thrsim,
  ZeroApps.thrs,
  ZeroApps.loads,
  ZeroApps.grafana,
  ZeroApps.domestic,
  ZeroApps.sailSystem,
]);

const envIncludedApps = String(import.meta.env.VITE_INCLUDE_APPS)
  .split(",")
  .map((s) => s.trim())
  .filter((s): s is ZeroApps => VALID_APPS.has(s as ZeroApps));

export const INCLUDED_APPS: ZeroApps[] = envIncludedApps.length
  ? [...new Set(envIncludedApps)]
  : DEFAULT_INCLUDED_APPS;
