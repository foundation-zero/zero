import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { DOCUMENTATION } from "./documentation";
import { MIMICS } from "./mimics";
import { PARAMETERS } from "./parameters";

// Rendered by the layout below the main navigation, with `SubNavigationProps`.
const SUB_NAVIGATION = defineAsyncComponent(
  () => import("@/modules/thrapp/components/sub-navigation/SubNavigation.vue"),
);

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
        subNavigation: SUB_NAVIGATION,
        views: MIMICS,
      },
    },
    {
      path: "control/:module",
      name: "thrs/control",
      component: () => import("@/modules/thrapp/views/Control.vue"),
      meta: {
        subNavigation: SUB_NAVIGATION,
        views: PARAMETERS,
      },
    },
    {
      path: "documentation/:module",
      name: "thrs/documentation",
      component: () => import("@/modules/thrapp/views/Documentation.vue"),
      meta: {
        subNavigation: SUB_NAVIGATION,
        views: DOCUMENTATION,
      },
    },
  ],
};
