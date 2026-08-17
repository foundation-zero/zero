import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const sharedRoutes: RouteRecordRaw = {
  path: "/",
  meta: {
    requiresAuth: false,
    layout: defineAsyncComponent(() => import("../layouts/SplashLayout.vue")),
  },
  component: () => import("@/modules/common/views/SplashScreen.vue"),
};

export const grafanaRoute: RouteRecordRaw = {
  path: "/grafana",
  name: "grafana",
  meta: {
    requiresAuth: false,
    layout: defineAsyncComponent(() => import("../layouts/SplashLayout.vue")),
  },
  component: () => import("@/modules/common/views/Grafana.vue"),
};

export const sailSystemRoute: RouteRecordRaw = {
  path: "/sail-system",
  name: "sail-system",
  meta: {
    requiresAuth: false,
    layout: defineAsyncComponent(() => import("../layouts/EmptyLayout.vue")),
  },
  component: () => import("@/modules/common/views/SailSystem.vue"),
};

export const getRootRoute = (route: string = "") => route.split(":")[0];
