import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { INCLUDED_APPS, ZeroApps } from "./apps";
import { grafanaRoute, sailSystemRoute, sharedRoutes } from "./modules/common/router";
import { domesticRoutes } from "./modules/domestic/router";
import { loadsRoutes } from "./modules/loads/router";
import { powerRoutes } from "./modules/power-tags/router";
import { heatSystemRoutes } from "./modules/heat-system/router";
import { heatSystemSimulationRoutes } from "./modules/heat-system-simulation/router";

const appRoutes: Record<ZeroApps, RouteRecordRaw> = {
  [ZeroApps.grafana]: grafanaRoute,
  [ZeroApps.sailSystem]: sailSystemRoute,
  [ZeroApps.heatSystemSimulation]: heatSystemSimulationRoutes,
  [ZeroApps.domestic]: domesticRoutes,
  [ZeroApps.loads]: loadsRoutes,
  [ZeroApps.heatSystem]: heatSystemRoutes,
  [ZeroApps.powerTags]: powerRoutes,
};

const includedRoutes = INCLUDED_APPS.map((app) => appRoutes[app]);

const router = createRouter({
  history: createWebHistory(),
  routes: [sharedRoutes, ...includedRoutes],
});

export default router;
