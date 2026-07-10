import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const thrsimRoutes: RouteRecordRaw = {
  path: "/thrsim",
  redirect: () => ({ name: "thrsim/mimic", query: {}, params: { module: "dhw" } }),
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/thrs/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  children: [
    {
      path: "simulation",
      name: "thrsim/simulation",
      component: () => import("@/modules/thrs/views/Simulation.vue"),
    },
    {
      path: ":module",
      children: [
        {
          path: "controls",
          name: "thrsim/controls",
          component: () => import("@/modules/thrs/views/Controls.vue"),
        },
        {
          path: "monitoring",
          name: "thrsim/monitoring",
          component: () => import("@/modules/thrs/views/Monitoring.vue"),
        },
        {
          path: "parameters",
          name: "thrsim/parameters",
          component: () => import("@/modules/thrs/views/Parameters.vue"),
        },
        {
          path: "mimic",
          name: "thrsim/mimic",
          component: () => import("@/modules/thrs/views/Mimic.vue"),
        },
      ],
    },
  ],
};
