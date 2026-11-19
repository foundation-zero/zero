import { ENV } from "@/settings";

/** Dashboards the splash screen links to, as paths on the deployment's Grafana (VITE_GRAFANA_URL). */
export const GRAFANA_DASHBOARDS = {
  "energy-monitoring": "/dashboards/f/eg2le2g6tvbb4b/?orgId=1",
  hydrogeneration:
    "/d/commissioning-hydrogeneration/hydrogeneration-and-propulsion?from=now-6h&to=now&timezone=browser&var-datasource=P6A33BD2DBCC29C4B&var-avg_window=5m",
  commissioning: "/dashboards/f/eg2le2fx99blsf/?orgId=1",
} as const;

export type GrafanaDashboard = keyof typeof GRAFANA_DASHBOARDS;

const isGrafanaDashboard = (name: string): name is GrafanaDashboard =>
  Object.prototype.hasOwnProperty.call(GRAFANA_DASHBOARDS, name);

/**
 * The Grafana URL to embed: a named dashboard, or Grafana's home page for no or an unknown name.
 * Empty when Grafana isn't configured.
 */
export const grafanaUrl = (dashboard?: string, baseUrl = ENV.VITE_GRAFANA_URL ?? "") => {
  const base = baseUrl.trim().replace(/\/+$/, "");
  if (!base) return "";
  return dashboard && isGrafanaDashboard(dashboard)
    ? `${base}${GRAFANA_DASHBOARDS[dashboard]}`
    : base;
};
