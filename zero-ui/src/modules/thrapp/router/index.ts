import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { MIMICS } from "./mimics";
import { PARAMETERS } from "./parameters";

export const thrappRoutes: RouteRecordRaw = {
  path: "/thrs",
  name: "thrs",
  alias: "/thrapp",
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/thrapp/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  redirect: () => ({ path: "/thrs/mimics/dhw", query: {} }),
  children: [
    {
      path: "mimics/:module",
      name: "thrs/mimics",
      component: () => import("@/modules/thrapp/views/Mimic.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/thrapp/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/thrapp/components/control-actions/ControlActions.vue"),
        ),
        views: MIMICS,
      },
    },
    {
      path: "control/:module",
      name: "thrs/control",
      component: () => import("@/modules/thrapp/views/Control.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/thrapp/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/thrapp/components/control-actions/ControlActions.vue"),
        ),
        views: PARAMETERS,
      },
    },
  ],
};
