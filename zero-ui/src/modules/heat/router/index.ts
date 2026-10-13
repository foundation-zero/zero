import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { MIMICS } from "./mimics";
import { PARAMETERS } from "./parameters";

export const heatRoutes: RouteRecordRaw = {
  path: "/heat",
  name: "heat",
  alias: ["/heat-system", "/thrs", "/thrapp"],
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/heat/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  redirect: () => ({ path: "/heat/mimics/dhw", query: {} }),
  children: [
    {
      path: "mimics/:module",
      name: "heat/mimics",
      component: () => import("@/modules/heat/views/Mimic.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/heat/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/heat-simulation/components/ControlActions.vue"),
        ),
        views: MIMICS,
      },
    },
    {
      path: "control/:module",
      name: "heat/control",
      component: () => import("@/modules/heat/views/Control.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/heat/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/heat-simulation/components/ControlActions.vue"),
        ),
        views: PARAMETERS,
      },
    },
  ],
};
