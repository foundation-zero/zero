import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { MIMICS } from "./mimics";
import { PARAMETERS } from "./parameters";

export const heatSystemRoutes: RouteRecordRaw = {
  path: "/heat-system",
  name: "heat-system",
  alias: ["/thrs", "/thrapp"],
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/heat-system/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  redirect: () => ({ path: "/heat-system/mimics/dhw", query: {} }),
  children: [
    {
      path: "mimics/:module",
      name: "heat-system/mimics",
      component: () => import("@/modules/heat-system/views/Mimic.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/heat-system/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/heat-system-simulation/components/ControlActions.vue"),
        ),
        views: MIMICS,
      },
    },
    {
      path: "control/:module",
      name: "heat-system/control",
      component: () => import("@/modules/heat-system/views/Control.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/heat-system/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/heat-system-simulation/components/ControlActions.vue"),
        ),
        views: PARAMETERS,
      },
    },
  ],
};
