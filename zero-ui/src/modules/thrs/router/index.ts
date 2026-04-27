import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

const thrsChildRoutes: RouteRecordRaw[] = [
  {
    path: "hmi",
    name: "thrs/hmi",
    meta: {
      layout: defineAsyncComponent(() => import("@/modules/thrs/layouts/DefaultLayout.vue")),
      requiresAuth: false,
    },
    redirect: () => ({ path: "/thrs/hmi/overview", query: {} }),
    children: [
      {
        path: "overview",
        name: "thrs/hmi/overview",
        component: () => import("@/modules/thrs/views/Overview.vue"),
      },
      {
        path: "simulation",
        name: "thrs/hmi/simulation",
        component: () => import("@/modules/thrs/views/Simulation.vue"),
      },
      {
        path: ":module",
        children: [
          {
            path: "controls",
            name: "thrs/hmi/controls",
            component: () => import("@/modules/thrs/views/Controls.vue"),
          },
          {
            path: "monitoring",
            name: "thrs/hmi/monitoring",
            component: () => import("@/modules/thrs/views/Monitoring.vue"),
          },

          {
            path: "parameters",
            name: "thrs/hmi/parameters",
            component: () => import("@/modules/thrs/views/Parameters.vue"),
          },
        ],
      },
    ],
  },
];

export const thrsRoutes: RouteRecordRaw = {
  path: "/thrs",
  redirect: () => ({ name: "thrs/hmi", query: {} }),
  children: thrsChildRoutes,
};
