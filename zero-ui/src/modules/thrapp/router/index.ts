import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const thrappRoutes: RouteRecordRaw = {
  path: "/thrapp",
  name: "thrapp",
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/thrapp/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  redirect: () => ({ path: "/thrapp/mimics/dhw", query: {} }),
  children: [
    {
      path: "mimics/:module",
      name: "thrapp/mimics",
      component: () => import("@/modules/thrapp/views/Mimic.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/thrapp/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/thrs/components/ControlActions.vue"),
        ),
      },
    },
    {
      path: "control/:module",
      name: "thrapp/control",
      component: () => import("@/modules/thrapp/views/Control.vue"),
      meta: {
        toolbarLeft: defineAsyncComponent(
          () => import("@/modules/thrapp/components/navigation/ModuleTabs.vue"),
        ),
        toolbarRight: defineAsyncComponent(
          () => import("@/modules/thrs/components/ControlActions.vue"),
        ),
      },
    },
  ],
};
