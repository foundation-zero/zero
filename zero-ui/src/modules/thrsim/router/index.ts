import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const thrsimRoutes: RouteRecordRaw = {
  path: "/thrsim",
  redirect: () => ({ name: "thrsim/mimic", query: {}, params: { module: "dhw" } }),
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/thrsim/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  children: [
    {
      path: "simulation",
      name: "thrsim/simulation",
      component: () => import("@/modules/thrsim/views/Simulation.vue"),
    },
    {
      path: ":module",
      children: [
        {
          path: "controls",
          name: "thrsim/controls",
          component: () => import("@/modules/thrsim/views/Controls.vue"),
        },
        {
          path: "monitoring",
          name: "thrsim/monitoring",
          component: () => import("@/modules/thrsim/views/Monitoring.vue"),
        },
        {
          path: "parameters",
          name: "thrsim/parameters",
          component: () => import("@/modules/thrsim/views/Parameters.vue"),
        },
        {
          path: "mimic",
          name: "thrsim/mimic",
          component: () => import("@/modules/thrapp/views/Mimic.vue"),
        },
      ],
    },
  ],
};
