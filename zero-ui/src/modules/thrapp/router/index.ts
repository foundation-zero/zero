import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

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
          () => import("@/modules/thrsim/components/ControlActions.vue"),
        ),
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
          () => import("@/modules/thrsim/components/ControlActions.vue"),
        ),
      },
    },
  ],
};
