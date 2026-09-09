import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { INCLUDED_APPS, ZeroApps } from "./apps";
import { grafanaRoute, sailSystemRoute, sharedRoutes } from "./modules/common/router";
import { domesticRoutes } from "./modules/domestic/router";
import { loadsRoutes } from "./modules/loads/router";
import { powerRoutes } from "./modules/power-tags/router";
import { thrappRoutes } from "./modules/thrapp/router";
import { thrsimRoutes } from "./modules/thrsim/router";

const appRoutes: Record<ZeroApps, RouteRecordRaw> = {
  [ZeroApps.grafana]: grafanaRoute,
  [ZeroApps.sailSystem]: sailSystemRoute,
  [ZeroApps.thrsim]: thrsimRoutes,
  [ZeroApps.domestic]: domesticRoutes,
  [ZeroApps.loads]: loadsRoutes,
  [ZeroApps.thrs]: thrappRoutes,
  [ZeroApps.powerTags]: powerRoutes,
};

const includedRoutes = INCLUDED_APPS.map((app) => appRoutes[app]);

const router = createRouter({
  history: createWebHistory(),
  routes: [sharedRoutes, ...includedRoutes],
});

export default router;
